import json
import time
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
from flask import Flask, render_template, request
import score
import env
from operator import itemgetter
import database


flask_app = Flask(__name__, template_folder='templates')


def setup_logging():
    logging_level = logging.INFO
    handler = RotatingFileHandler('web.log', maxBytes=100000, backupCount=1)
    handler.setLevel(logging_level)
    flask_app.logger.addHandler(handler)
    flask_app.logger.setLevel(logging_level)


def wsgi_app(*args, **kwargs):
    # Don't want to setup logging when `web.py` is imported
    setup_logging()
    return flask_app(*args, **kwargs)


def bench_mark(f):
    @wraps(f)  # required
    def inner(*args, **kwargs):
        it = time.time()
        result = f(*args, **kwargs)
        flask_app.logger.info('function %s took %f seconds' % (f.__name__, time.time() - it))
        return result
    return inner


@flask_app.route('/search', methods=['POST'])
@bench_mark  # this has no effect if decorated above `route`
def search():
    query = request.form['search-query']
    return json.dumps(database.search_tweet(query))


def get_scores():
    """
    単語ごとのスコアを入れ子のリストとして返す
    辞書型で返してしまうとソート出来ない
    """
    scores = score.score_key_phrases(save=False)
    return sorted(scores.items(), key=itemgetter(1), reverse=True)


predefined_frequencies = []


@flask_app.route('/', methods=['GET'])
@bench_mark
def home():
    if predefined_frequencies:
        frequencies = predefined_frequencies
    else:
        frequencies = get_scores()
        # printing all the frequencies is way too slow
        cap = 50
        frequencies = frequencies[:cap]
    flask_app.logger.info('frequencies: ' + str(frequencies))
    return render_template('index.html', frequencies=frequencies)


def run_dev(frequencies=None):
    global predefined_frequencies
    predefined_frequencies = frequencies or []
    setup_logging()
    flask_app.run(debug=env.get_debug(), host='0.0.0.0', port=env.get_web_port())


if __name__ == '__main__':
    run_dev()
