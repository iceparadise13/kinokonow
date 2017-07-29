import logging
from celery import Celery, chain
from celery.schedules import crontab
from kinokonow import database, env, preprocess, tweet, ma, score, words, log as knlog


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
    return hash_tags + ma.extract_nouns_from_ma_server(tweet, host=host, port=port)


@celery.task
def save_nouns(nouns):
    if nouns:
        database.save_nouns(nouns)


def create_noun_extraction_task(tweet):
    return chain(preprocess_tweet.s(tweet), extract_nouns.s(), save_nouns.s())


@celery.task
def hourly_task():
    """定期タスクとしてchainが使えないみたいなので一つのタスクとして定義する"""
    scores = score.score_key_phrases(save=True)
    logger.info('tfidf scores ' + str(scores))
    if scores:
        # 値が0の要素があるとゼロ除算が起きるので事前に除く
        scores = dict([(k, v) for k, v in scores.items() if v])
        img = words.generate_word_cloud(scores, font_path='font.ttf')
        tweet.tweet_media(img)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute=env.get_tweet_minute()), hourly_task, name='tweet every hour')
