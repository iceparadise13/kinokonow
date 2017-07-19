from datetime import datetime, timedelta
from celery import Celery, chain
from celery.schedules import crontab
import database
import env
import preprocess
import tfidf
from ma import extract_nouns_from_ma_server
from web import flask_app
import tweet
import words


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


def score_key_phrases():
    """
    保存されている名詞のtfidf値を計算して返す
    単一ツイートの名詞を一つのドキュメントとして扱うとツイートの長さの性質上、
    tfidfが低頻出語を抽出するだけのアルゴリズムになってしまうので、
    一定の時系列の範囲中にあるツイートの名詞全てを一つのドキュメントとして扱う
    ドキュメントをidf用の過去のドキュメントに含めてしまうと一番最初のドキュメントを取得した時に
    全ての単語のidfスコアが0になってワードクラウドが出力出来ないのでドキュメントの保存は最後に行う
    :return:
    tfidf値の辞書
    実数のスコアはそのままwordcloudライブラリのクラウド生成メソッドに渡しても問題無い
    """
    now = datetime.utcnow()
    document = database.get_noun_frequencies(now - timedelta(hours=1))
    if not document:
        print('Failed to get noun frequencies')
        return {}
    past_documents = database.get_documents(now - timedelta(days=3))
    scores = tfidf.score(document, past_documents)
    database.save_document(document, now)
    return scores


@celery.task
def hourly_task():
    """定期タスクとしてchainが使えないみたいなので一つのタスクとして定義する"""
    scores = score_key_phrases()
    print('tfidf scores ' + str(scores))
    if scores:
        # 値が0の要素があるとゼロ除算が起きるので事前に除く
        scores = dict([(k, v) for k, v in scores.items() if v])
        img = words.generate_word_cloud(scores, font_path='font.ttf')
        tweet.tweet_word_cloud(img)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute=env.get_tweet_minute()), hourly_task, name='tweet every hour')
