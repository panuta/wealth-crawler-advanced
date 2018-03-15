import traceback

import falcon
import json

from server.controller.models import Spider


class CrawlerResource:
    def on_get(self, request, response):
        """ Get crawler status
        """

        response.body = json.dumps({
            'status': 'success',
            'spiders': Spider.spiders_dict(),
            'jobs': [],
            'logs': [],
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
