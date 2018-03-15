import requests

from server import config
from server.celery_app import app


@app.task
def crawl(project_name, spider_name, job_id):
    resp = requests.post('{scrapyd_url}/schedule.json'.format(scrapyd_url=config.SCRAPYD_URL), params={
        'project': project_name,
        'spider': spider_name,
        'job_id': job_id,
    })

    resp_json = resp.json()

    if resp_json.get('status', '') != 'ok':
        # TODO : test exception
        raise Exception('Scrapyd response with error: {}', resp_json.get('message', ''))
