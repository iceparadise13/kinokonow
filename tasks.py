import os
import tempfile
import uuid
from datetime import datetime, timedelta
from celery import Celery, chain
from celery.schedules import crontab
from twython import Twython
import mongo
from web import flask_app
import words
import preprocess
from ma import extract_nouns_from_ma_server
import env
import settings


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


def create_noun_extraction_task(tweet):
    return chain(preprocess_tweet.s(tweet), extract_nouns.s())


def get_api():
    return Twython(*settings.get_twython_settings())


def generate_temp_file_name():
    return os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))


class ImageFileContext(object):
    """
    Context that takes an image, saves it as a temp file and returns the file object
    It'd be better if I could just derive a BytesIO object from `image` but I can't get it to upload
    """
    def __init__(self, image):
        image_file_name = generate_temp_file_name()
        image.save(image_file_name, format='png')
        self.image_file = open(image_file_name, 'rb')

    def __enter__(self):
        return self.image_file

    def __exit__(self, *args, **kwargs):
        return self.image_file.close()


@celery.task
def tweet_word_cloud():
    db = mongo.connect()
    frequencies = words.get_filtered_noun_frequencies(
        db.nouns, datetime.utcnow() - timedelta(hours=1), words.read_black_list())
    if not frequencies:
        return
    img = words.generate_word_cloud(frequencies, font_path='font.ttf')
    # Instantiate every time to avoid connection reset
    api = get_api()
    with ImageFileContext(img) as image_file:
        media_id = api.upload_media(media=image_file)['media_id']
    api.update_status(status='a', media_ids=[media_id])


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute=0), tweet_word_cloud.s(), name='tweet every hour')
