import requests
from dateutil.parser import parse

from server import config
from server.celery_app import app
from server.controller.models import Project, SpiderJobLog


def _update_job_log(task_id, **kwargs):
    try:
        job_log = SpiderJobLog.get(task_id=task_id)
    except SpiderJobLog.DoesNotExist:
        pass
    else:
        for key, value in kwargs.items():
            setattr(job_log, key, value)

        job_log.save()


@app.task
def listjobs():
    projects = Project.select()

    for project in projects:
        response = requests.get('{scrapyd_url}/listjobs.json'.format(scrapyd_url=config.SCRAPYD_URL), params={
            'project': project.project_name,
        })

        response_json = response.json()

        if response_json.get('status', '') != 'ok':
            raise Exception('Scrapyd response with error: {}', response_json.get('message', ''))

        for task in response_json.get('pending'):
            _update_job_log(task.get('id'), status='pending')

        for task in response_json.get('running'):
            date_started = parse(task['start_time'])
            _update_job_log(task.get('id'), status='running', date_started=date_started)

        for task in response_json.get('finished'):
            date_finished = parse(task['end_time'])
            _update_job_log(task.get('id'), status='finished', date_finished=date_finished)
