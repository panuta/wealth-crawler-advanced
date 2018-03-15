from datetime import datetime

import shortuuid

from celery.schedules import crontab
from redbeat import RedBeatSchedulerEntry
from redbeat.schedulers import RedBeatConfig

from server import config
from server.celery_app import app
from server.controller.models import SpiderJob, Spider
from server.tasks.spiders import crawl
from server.utils import crontab_hour_to_utc


def create_job(spider_name, schedule=None, parameters=None):
    now = datetime.now()
    job_id = '{}-{}'.format(now.strftime('%Y%m%d'), shortuuid.uuid())

    return SpiderJob.create(
        job_id=job_id,
        spider_name=spider_name,
        schedule=schedule,
        parameters=parameters,
        date_added=now,
    )


def run_job(job):
    """ Run this job immediately if this job doesn't have a schedule,
        If this job has a schedule, schedule it to run.
    """

    spider = Spider.get(Spider.name == job.spider_name)
    project_name = spider.project_name

    if job.schedule:
        minute, hour, day_of_week, day_of_month, month_of_year = job.schedule.split(' ')
        utc_hour = crontab_hour_to_utc(hour, config.CRONTAB_TIMEZONE)
        interval = crontab(minute, utc_hour, day_of_week, day_of_month, month_of_year)

        entry = RedBeatSchedulerEntry(job.job_id, 'server.tasks.spiders.crawl', interval, kwargs={
            'project': project_name,
            'spider': job.spider_name,
            'job_id': job.job_id,
            'parameters': job.parameters,
        }, app=app)

        entry.save().reschedule()

    else:
        crawl.delay(project_name, job.spider_name, job.job_id, job.parameters)


def _get_entry_from_job(job):
    conf = RedBeatConfig(app)
    return RedBeatSchedulerEntry.from_key('{}{}'.format(conf.key_prefix, job.job_id), app=app)


def reschedule_job(job, schedule):
    try:
        entry = _get_entry_from_job(job)
    except KeyError:
        pass
    else:
        minute, hour, day_of_week, day_of_month, month_of_year = schedule.split(' ')
        utc_hour = crontab_hour_to_utc(hour, config.CRONTAB_TIMEZONE)
        interval = crontab(minute, utc_hour, day_of_week, day_of_month, month_of_year)

        entry.schedule = interval
        entry.save().reschedule(last_run_at=0)

        job.schedule = schedule
        job.save()


def stop_job(job):
    try:
        entry = _get_entry_from_job(job)
    except KeyError:
        pass
    else:
        entry.delete()


def delete_job(job):
    stop_job(job)
    job.delete_instance()
