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

# crawler_scheduled_resource = spiders_app.CrawlerScheduledResource()
# api.add_route('/crawler/jobs/scheduled', crawler_scheduled_resource)
#
# crawler_logs_resource = spiders_app.CrawlerLogsResource()
# api.add_route('/crawler/jobs/logs', crawler_logs_resource)
#
# spider_resource = spiders_app.SpiderResource()
# api.add_route('/spider', spider_resource)
#
# spider_job_resource = spiders_app.SpiderJobResource()
# api.add_route('/spider/job', spider_job_resource)
#
# spider_job_logs_resource = spiders_app.SpiderJobLogsResource()
# api.add_route('/spider/job/logs', spider_job_logs_resource)





# spider_jobs_resource = spiders_app.SpiderJobsResource()
# api.add_route('/spider/jobs', spider_jobs_resource)



# spider_scheduled_resource = spiders_app.SpiderScheduledResource()
# api.add_route('/spider/scheduled', spider_scheduled_resource)


