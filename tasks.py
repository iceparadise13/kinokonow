import re
import json
from datetime import datetime
import requests
from celery import Celery, chain
import pymongo
from web import flask_app


flask_app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
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
mongo_client = pymongo.MongoClient(host='localhost', port=27017)
db = mongo_client.get_database('kinokonow')


def remove_pattern(pat, text):
    return re.sub('%s(?:\s|$)' % pat, '', text)


def remove_mention(text):
    return remove_pattern('@.+?', text)


def remove_url(text):
    return remove_pattern('(?:http|https)://.+?', text)


def remove_rt_boilerplate(text):
    return remove_pattern('RT @.+:', text)


def clean(text):
    text = remove_rt_boilerplate(text)
    text = remove_url(text)
    return remove_mention(text)


@celery.task()
def clean_tweet(tweet):
    return clean(tweet)


class YahooApi(object):
    def __init__(self, api_key, session=None):
        self.api_key = api_key
        self.session = session or requests.Session()

    def extract_phrases(self, text):
        pat = 'https://jlp.yahooapis.jp/KeyphraseService/V1/extract?appid=%s&output=json&sentence=%s'
        resp = self.session.get(pat % (self.api_key, text))
        result = json.loads(resp.content.decode('utf-8'))
        if type(result) == dict:
            return list(result.keys())
        return []


@celery.task()
def extract_nouns(corpus, api_key):
    api = YahooApi(api_key)
    nouns = api.extract_phrases(corpus)
    if nouns:
        db.nouns.insert_many([{'text': n, 'created_at': datetime.utcnow()} for n in nouns])


def create_noun_extraction_task(yahoo_api_key, tweet):
    return chain(clean_tweet.s(tweet),
                 extract_nouns.s(yahoo_api_key))
