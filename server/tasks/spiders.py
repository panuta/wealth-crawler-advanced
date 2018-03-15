import requests

from server import config
from server.celery_app import app
from server.controller.models import SpiderJobLog


@app.task
def crawl(project_name, spider_name, job_id, parameters=None):
    resp = requests.post('{scrapyd_url}/schedule.json'.format(scrapyd_url=config.SCRAPYD_URL), params={
        'project': project_name,
        'spider': spider_name,
        'job_id': job_id,
    })

    # TODO : send parameters

    resp_json = resp.json()

    if resp_json.get('status', '') != 'ok':
        raise Exception('Scrapyd response with error: {}', resp_json.get('message', ''))

    log = SpiderJobLog(
        job_id=job_id,
        spider_name=spider_name,
        parameters=parameters,
        task_id=resp_json.get('jobid'),
    )
    log.save()
