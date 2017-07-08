import pymongo
from datetime import datetime, timedelta
from flask import Flask, render_template
from operator import itemgetter
import words
from celery import Celery


flask_app = Flask(__name__, template_folder='templates')
flask_app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
client = pymongo.MongoClient(host='localhost', port=27017)
db = client.get_database('kinokonow')


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


@celery.task()
def add_together(a, b):
    return a + b


@flask_app.route('/')
def home():
    frequencies = words.get_filtered_noun_frequencies(
        db.nouns, datetime.utcnow() - timedelta(hours=1), words.read_black_list())
    frequencies = [[k, v] for k, v in frequencies.items()]
    frequencies = sorted(frequencies, key=itemgetter(1), reverse=True)[:50]
    return render_template('index.html', frequencies=frequencies)


if __name__ == '__main__':
    flask_app.run(debug=True, host='0.0.0.0')
