import json
import logging
import os
import time
from datetime import timezone
from functools import wraps
from logging.handlers import RotatingFileHandler
from operator import itemgetter
from flask import Flask, render_template, request
from kinokonow import env, score, database
from kinokonow.search import normalize_search_query


script_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.join(script_dir, os.path.pardir)
flask_app = Flask(__name__,
                  template_folder=os.path.join(parent_dir, 'templates'),
                  static_folder=os.path.join(parent_dir, 'static'))


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


def prepare_search_results(cursor, cap):
    # by default `datetime` objects returned by pymongo have no timezones associated with them
    # these objects are then assumed to be the localtime, rendering the return of `timestamp` inaccurate
    # `mongomock` does not have the same behavior so this is currently not unit-testable
    return [{'text': c['text'], 'user': c['user']['name'],
             'created_at': c['created_at'].replace(tzinfo=timezone.utc).timestamp()}
             for c in list(cursor[:cap])]


mock_search = None


@flask_app.route('/search', methods=['POST'])
@bench_mark  # this has no effect if decorated above `route`
def search():
    if mock_search:
        search_results = mock_search()
    else:
        query = request.form['search-query']
        query = normalize_search_query(query)
        search_results = database.search_tweet(query)
        search_results = prepare_search_results(search_results, cap=50)
    return json.dumps(search_results)


def get_scores():
    """
    単語ごとのスコアを降順ソートされた入れ子のリストとして返す
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


def run_dev(frequencies=None, search=None):
    global predefined_frequencies
    predefined_frequencies = frequencies or []
    global mock_search
    mock_search = search or []
    setup_logging()
    flask_app.run(debug=env.get_debug(), host='0.0.0.0', port=env.get_web_port())


if __name__ == '__main__':
    run_dev()
