import logging
from celery import Celery, chain
from celery.schedules import crontab
from kinokonow import database, env, filter, tweet, ma, score, word_cloud, log as knlog


# wsgiアプリでログをstdoutに出力するのは非推奨らしいのでflaskでこのモジュールをインポートしてはいけない
knlog.setup_worker()
logger = logging.getLogger(__name__)


def make_celery():
    redis_host = env.get_redis_host()
    redis_port = env.get_redis_port()
    redis_url = 'redis://%s:%d' % (redis_host, redis_port)
    return Celery('worker', backend=redis_url, broker=redis_url)


celery = make_celery()


@celery.task
def save_tweet(data):
    database.save_tweet(data)


@celery.task
def extract_phrases(tweet):
    """
    形態素解析鯖を使って与えられたツイートからフレーズを抽出する
    ハッシュタグは無条件でフレーズとして扱う
    フレーズの重複は許可しない
    :param data: ツイートとハッシュタグのリストのタプル
    :return: 抽出されたフレーズのリスト
    """
    tweet, hash_tags = filter.pre_ma(tweet)
    host = env.get_ma_host()
    port = env.get_ma_port()
    return set(hash_tags + ma.extract_phrases_from_ma_server(tweet, host=host, port=port))


@celery.task
def save_phrases(phrases):
    if phrases:
        database.save_phrases(phrases)


def create_phrase_extraction_task(tweet):
    return chain(extract_phrases.s(tweet), save_phrases.s())


@celery.task
def hourly_task():
    """定期タスクとしてchainが使えないみたいなので一つのタスクとして定義する"""
    scores = score.score_key_phrases(save=True)
    logger.info('tfidf scores ' + str(scores))
    if scores:
        # 値が0の要素があるとゼロ除算が起きるので事前に除く
        scores = dict([(k, v) for k, v in scores.items() if v])
        img = word_cloud.generate(scores, font_path='font.ttf')
        tweet.tweet_media(img)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute=env.get_tweet_minute()), hourly_task, name='tweet every hour')
