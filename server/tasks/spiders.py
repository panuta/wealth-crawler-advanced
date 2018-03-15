import requests

from server import config
from server.celery_app import app
from server.controller.models import SpiderJobLog


@app.task
def crawl(project, spider, job_id, parameters=None):
    resp = requests.post('{scrapyd_url}/schedule.json'.format(scrapyd_url=config.SCRAPYD_URL), params={
        'project': project,
        'spider': spider,
        'job_id': job_id,
        **parameters,
    })

    response_json = resp.json()

    if response_json.get('status', '') != 'ok':
        raise Exception('Scrapyd response with error: {}', response_json.get('message', ''))

    log = SpiderJobLog(
        job_id=job_id,
        spider_name=spider,
        parameters=parameters,
        task_id=response_json.get('jobid'),
    )
    log.save()
