import json

from peewee import Model, CharField, DateTimeField

from server.utils import datetime_to_str
from ..database import db


class Project(Model):
    project_name = CharField()

    class Meta:
        database = db


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
    schedule = CharField(null=True)  # Crontab value, if empty means run once
    date_added = DateTimeField()

    class Meta:
        database = db

    @classmethod
    def jobs_scheduled_dict(cls, spider_name=None):
        if spider_name:
            jobs = SpiderJob.select().where(SpiderJob.spider_name == spider_name, ~(SpiderJob.schedule >> None))
        else:
            jobs = SpiderJob.select().where(~(SpiderJob.schedule >> None))
        return [job.to_dict() for job in jobs]

    def to_dict(self):
        return {
            'job_id': self.job_id,
            'spider_name': self.spider_name,
            'parameters': self.parameters,
            'schedule': self.schedule,
            'date_added': datetime_to_str(self.date_added),
        }

    @property
    def parameters(self):
        return json.loads(self.parameters_json) if self.parameters_json else {}

    @parameters.setter
    def parameters(self, parameters_dict):
        self.parameters_json = json.dumps(parameters_dict)


class SpiderJobLog(Model):
    job_id = CharField()
    spider_name = CharField()
    parameters = CharField(null=True)
    task_id = CharField(null=True)
    status = CharField(null=True)
    date_started = DateTimeField(null=True)
    date_finished = DateTimeField(null=True)

    class Meta:
        database = db

    def to_dict(self):
        return {
            'job_id': self.job_id,
            'spider_name': self.spider_name,
            'parameters': self.parameters,
            'task_id': self.task_id,
            'status': self.status,
            'date_started': datetime_to_str(self.date_started),
            'date_finished': datetime_to_str(self.date_finished),
        }

    @classmethod
    def logs_dict(cls, job_id=None):
        if job_id:
            logs = SpiderJobLog.select().where(SpiderJobLog.job_id == job_id)
        else:
            logs = SpiderJobLog.select()
        return [log.to_dict() for log in logs]


db.create_tables([
    Project,
    Spider,
    SpiderJob,
    SpiderJobLog,
], safe=True)
