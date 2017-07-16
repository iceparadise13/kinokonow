import os
import re
import tempfile
import uuid
from datetime import datetime, timedelta
from celery import Celery, chain
from celery.schedules import crontab
from twython import Twython
import mongo
from pyknp import Jumanpp
from web import flask_app
import words
from util import load_yaml


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
settings = load_yaml('settings.yml')


def remove_pattern(pat, text):
    return re.sub('%s(?:\s|$)' % pat, '', text)


def remove_mention(text):
    return remove_pattern('@.+?', text)


def remove_url(text):
    return remove_pattern('(?:http|https)://.+?', text)


def remove_rt_boilerplate(text):
    return remove_pattern('RT @.+:', text)


@celery.task
def preprocess_tweet(tweet):
    # 半角スペースが入っているとJumanppの挙動がおかしくなるので消す
    tweet = tweet.replace(' ', '')
    # 文章的に意味を持たないツイッター固有の情報を消す
    tweet = remove_rt_boilerplate(tweet)
    tweet = remove_mention(tweet)
    tweet = remove_url(tweet)
    return tweet.split('\n')


def extract_nouns_from_sentence(sentence, analyzer):
    return [anal.midasi for anal in analyzer(sentence) if anal.hinsi == '名詞']


@celery.task
def extract_nouns(corpus, analyzer=None):
    analyzer = analyzer or (lambda sentence: Jumanpp().analysis(sentence).mrph_list())
    nouns = []
    for sentence in corpus.split('\n'):
        nouns += extract_nouns_from_sentence(sentence, analyzer)
    return nouns


def create_noun_extraction_task(tweet):
    return chain(preprocess_tweet.s(tweet), extract_nouns.s())


def get_api(settings):
    return Twython(
        settings['consumer_key'],
        settings['consumer_secret'],
        settings['access_token_key'],
        settings['access_token_secret'])


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
    db = mongo.connect(settings['mongo'])
    frequencies = words.get_filtered_noun_frequencies(
        db.nouns, datetime.utcnow() - timedelta(hours=1), words.read_black_list())
    if not frequencies:
        return
    img = words.generate_word_cloud(frequencies, font_path='font.ttf')
    # Instantiate every time to avoid connection reset
    api = get_api(settings['twitter'])
    with ImageFileContext(img) as image_file:
        media_id = api.upload_media(media=image_file)['media_id']
    api.update_status(status='a', media_ids=[media_id])


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute=0), tweet_word_cloud.s(), name='tweet every hour')
