from celery import Celery

app = Celery('celery_app', broker='redis://redis')
app.conf.update(
    beat_scheduler = 'redbeat.RedBeatScheduler',
    beat_max_loop_interval=5,  # 5 seconds
    redbeat_lock_key=None,
    redbeat_lock_timeout=5
)
