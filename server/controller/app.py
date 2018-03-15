import traceback

import falcon
import json

from crontab import CronSlices

from server.controller.functions.job import create_job, run_job, delete_job
from server.controller.models import Spider, SpiderJob, SpiderJobLog


class CrawlerResource:
    def on_get(self, request, response):
        """ Get crawler status
        """

        response.body = json.dumps({
            'status': 'success',
            'spiders': Spider.spiders_dict(),
            'jobs': {
                'scheduled': SpiderJob.jobs_scheduled_dict(),
            },
            'logs': SpiderJobLog.logs_dict(),
        })
        response.status = falcon.HTTP_200

    def on_put(self, request, response):
        """ Deploy spiders from git repository
        """
        clone_url = request.get_param('clone_url', True)
        branch = request.get_param('branch')

        from server.controller.functions.deploy import deploy

        try:
            deploy(clone_url, branch)
        except Exception as e:
            response.body = json.dumps({'status': 'error', 'message': str(e), 'traceback': traceback.format_exc()})
            response.status = falcon.HTTP_200
            return

        response.body = json.dumps({'status': 'success'})
        response.status = falcon.HTTP_200


class SpiderResource:
    def on_get(self, request, response):
        """ Get spider data by spider name
        """
        spider_name = request.get_param('spider_name', True)

        try:
            spider = Spider.get(Spider.name == spider_name)
        except Spider.DoesNotExist:
            response.body = json.dumps(
                {'status': 'error', 'message': 'Cannot find spider named {}'.format(spider_name)})
            response.status = falcon.HTTP_200
            return

        response.body = json.dumps({
            'status': 'success',
            'spider': spider.to_dict()
        })
        response.status = falcon.HTTP_200


class SpiderJobResource:
    JOB_PARAMETER_RESERVED_KEYWORDS = {'project', 'spider', 'job_id'}

    def on_get(self, request, response):
        """
        Get job by job_id
        """

        job_id = request.get_param('job_id', True)

        try:
            job = SpiderJob.get(SpiderJob.job_id == job_id)
        except SpiderJob.DoesNotExist:
            response.body = json.dumps({'status': 'error', 'message': 'Cannot find job with id={}'.format(job_id)})
            response.status = falcon.HTTP_200
            return

        response.body = json.dumps({
            'status': 'success',
            'job': job.to_dict()
        })
        response.status = falcon.HTTP_200

    def on_put(self, request, response):
        """
        Create a new job
        """

        spider_name = request.get_param('spider_name', True)
        schedule = request.get_param('schedule')

        parameters = request.params

        try:
            del parameters['spider_name']
            del parameters['schedule']
        except KeyError:
            pass

        # Check parameters
        if set(parameters.keys()) & SpiderJobResource.JOB_PARAMETER_RESERVED_KEYWORDS:
            response.body = json.dumps(
                {'status': 'error',
                 'message': 'Parameter must not be in reserved keywords {}'.format(
                     SpiderJobResource.JOB_PARAMETER_RESERVED_KEYWORDS)})
            response.status = falcon.HTTP_200
            return

        # Check spider
        try:
            spider = Spider.get(Spider.name == spider_name)
        except Spider.DoesNotExist:
            response.body = json.dumps({'status': 'error', 'message': 'Cannot find spider by this name'})
            response.status = falcon.HTTP_200
            return

        # Check schedule
        if not CronSlices.is_valid(schedule):
            response.body = json.dumps({'status': 'error', 'message': 'Invalid schedule format'})
            response.status = falcon.HTTP_200
            return

        try:
            job = create_job(spider_name, schedule, parameters)
        except Exception as e:
            response.body = json.dumps({'status': 'error', 'message': 'Cannot create job: {}'.format(str(e))})
            response.status = falcon.HTTP_200
            return

        try:
            run_job(job)
        except Exception as e:
            response.body = json.dumps({
                'status': 'error',
                'message': 'Cannot run job: {}'.format(str(e)),
                'traceback': traceback.format_exc()})
            response.status = falcon.HTTP_200
            return

        response.body = json.dumps({
            'status': 'scheduled',
            'job_id': job.job_id
        })
        response.status = falcon.HTTP_200

    def on_delete(self, request, response):
        job_id = request.get_param('job_id', True)

        if job_id == 'all':
            jobs = SpiderJob.select()
        else:
            try:
                job = SpiderJob.get(SpiderJob.job_id == job_id)
            except SpiderJob.DoesNotExist:
                response.body = json.dumps({'status': 'error', 'message': 'Cannot find job by this id'})
                response.status = falcon.HTTP_200
                return

            jobs = [job]

        for job in jobs:
            delete_job(job)

        response.body = json.dumps({'status': 'success'})
        response.status = falcon.HTTP_200
