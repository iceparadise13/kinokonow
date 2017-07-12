import os
import re
import json
import tempfile
import uuid
from datetime import datetime, timedelta
import requests
import yaml
from celery import Celery, chain
from twython import Twython
import pymongo
from web import flask_app
import words


redis_host = 'redis'
redis_url = 'redis://%s:6379' % redis_host
flask_app.config.update(
    CELERY_BROKER_URL=redis_url,
    CELERY_RESULT_BACKEND=redis_url
)


def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


celery = make_celery(flask_app)
mongo_client = pymongo.MongoClient(host='mongo', port=27017)
db = mongo_client.get_database('kinokonow')


@celery.task
def tweet_word_cloud(msg):
    print(msg)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, tweet_word_cloud.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, tweet_word_cloud.s('world'), expires=10)
