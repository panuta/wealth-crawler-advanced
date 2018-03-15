import json
import time
import uuid
from datetime import datetime

from peewee import Model, CharField, DateTimeField

from server.utils import datetime_to_str
from ..database import db


class Spider(Model):
    name = CharField()
    project_name = CharField()
    date_deployed = DateTimeField()

    class Meta:
        database = db

    @classmethod
    def spiders_dict(cls):
        return [spider.to_dict() for spider in Spider.select()]

    def to_dict(self):
        return {
            'name': self.name,
            'project_name': self.project_name,
            'date_deployed': datetime_to_str(self.date_deployed),
        }


class SpiderJob(Model):
    job_id = CharField()
    spider_name = CharField()
    parameters_json = CharField(null=True)
    config_json = CharField(null=True)
    schedule = CharField(null=True)  # Crontab value, if empty means run once
    date_added = DateTimeField()

    class Meta:
        database = db

    @classmethod
    def jobs_scheduled_dict(cls, spider_name):
        jobs = SpiderJob.select().where(SpiderJob.spider_name == spider_name, ~(SpiderJob.schedule >> None))
        return [job.to_dict() for job in jobs]

    def to_dict(self):
        return {
            'job_id': self.job_id,
            'spider_name': self.spider_name,
            'config': self.parameters,
            'schedule': self.schedule,
            'date_added': datetime_to_str(self.date_added),
        }

    @property
    def parameters(self):
        return json.loads(self.parameters_json)

    @parameters.setter
    def parameters(self, parameters_dict):
        self.parameters_json = json.dumps(parameters_dict)


class SpiderJobLog(Model):
    run_id = CharField()
    job_id = CharField()
    spider_name = CharField()
    parameters_json = CharField(null=True)
    schedule = CharField(null=True)  # Crontab value, if empty means run once
    finish_reason = CharField(null=True)
    date_finished = DateTimeField(null=True)

    class Meta:
        database = db

    @classmethod
    def logs_dict(cls, spider_name, job_id=None):
        if not job_id:
            logs = SpiderJobLog.select().where(SpiderJobLog.spider_name == spider_name)
        else:
            logs = SpiderJobLog.select().where(SpiderJobLog.spider_name == spider_name, SpiderJobLog.job_id == job_id)

        return [log.to_dict() for log in logs]

    def to_dict(self):
        return {
            'run_id': self.run_id,
            'job_id': self.job_id,
            'spider_name': self.spider_name,
            'parameters': self.parameters,
            'schedule': self.schedule,
            'finish_reason': self.finish_reason,
            'date_finished': datetime_to_str(self.date_finished) if self.date_finished else None,
        }

    @classmethod
    def create_log_from_job(cls, job):
        log = SpiderJobLog(
            run_id = '{}-{}'.format(int(time.time()), uuid.uuid4()),
            job_id = job.job_id,
            spider_name = job.spider_name,
            parameters_json = job.parameters_json,
            schedule = job.schedule,
        )
        log.save()
        return log

    def finish(self, reason=None):
        self.date_finished = datetime.now()
        self.finish_reason =  reason
        self.save()

    @property
    def parameters(self):
        return json.loads(self.parameters_json)

    @parameters.setter
    def parameters(self, parameters_dict):
        self.parameters_json = json.dumps(parameters_dict)


db.create_tables([
    Spider,
    SpiderJob,
    SpiderJobLog,
], safe=True)