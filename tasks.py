from celery import Celery, chain
from celery import Celery, chain
from celery.schedules import crontab

import database
import env
import preprocess
import tweet
import words
from ma import extract_nouns_from_ma_server
from score import score_key_phrases
from web import flask_app

redis_host = env.get_redis_host()
redis_port = env.get_redis_port()
redis_url = 'redis://%s:%d' % (redis_host, redis_port)
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


@celery.task
def preprocess_tweet(tweet):
    return preprocess.preprocess_tweet(tweet)


@celery.task
def extract_nouns(data):
    """
    形態素解析鯖を使って与えられたツイートから名詞を抽出する
    ハッシュタグは無条件で名詞として扱う
    :param data: ツイートとハッシュタグのリストのタプル
    :return: 抽出された名詞のリスト
    """
    tweet, hash_tags = data
    host = env.get_ma_host()
    port = env.get_ma_port()
    return hash_tags + extract_nouns_from_ma_server(tweet, host=host, port=port)


@celery.task
def save_nouns(nouns):
    if nouns:
        database.save_nouns(nouns)


def create_noun_extraction_task(tweet):
    return chain(preprocess_tweet.s(tweet), extract_nouns.s(), save_nouns.s())


@celery.task
def hourly_task():
    """定期タスクとしてchainが使えないみたいなので一つのタスクとして定義する"""
    scores = score_key_phrases(save=True)
    print('tfidf scores ' + str(scores))
    if scores:
        # 値が0の要素があるとゼロ除算が起きるので事前に除く
        scores = dict([(k, v) for k, v in scores.items() if v])
        img = words.generate_word_cloud(scores, font_path='font.ttf')
        tweet.tweet_media(img)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute=env.get_tweet_minute()), hourly_task, name='tweet every hour')
