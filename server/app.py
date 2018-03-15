import falcon
import json

from .controller import app as controller_app


def error_serializer(request, response, exception):
    result = {
        'status': 'error',
        'title': exception.title,
        'message': exception.description,
    }

    response.body = json.dumps(result)
    response.content_type = 'application/json'
    response.append_header('Vary', 'Accept')


api = application = falcon.API()
api.set_error_serializer(error_serializer)


# Crawler Resource
# ----------------------------------------------------------------------------

crawler_resource = controller_app.CrawlerResource()
api.add_route('/crawler', crawler_resource)

spider_resource = controller_app.SpiderResource()
api.add_route('/spider', spider_resource)

spider_job_resource = controller_app.SpiderJobResource()
api.add_route('/spider/job', spider_job_resource)
