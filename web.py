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


def scores_to_frequencies(scores, freq_range):
    if not scores:
        return []
    min_score = min(scores.values())
    max_score = max(scores.values())
    result = []
    for k, v in scores.items():
        score_range = max_score - min_score
        fraction = (v - min_score) / score_range if score_range else 0.5
        v = freq_range[0] + ((freq_range[1] - freq_range[0]) * fraction)
        result.append([k, int(v)])
    return result


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


@flask_app.route('/', methods=['GET'])
@bench_mark
def home():
    cap = 50
    scores = score.score_key_phrases(save=False)
    frequencies = scores_to_frequencies(scores, (1, 10))
    frequencies = sorted(frequencies, key=itemgetter(1), reverse=True)
    # printing all the frequencies is way too slow
    frequencies = frequencies[:cap]
    flask_app.logger.info('frequencies: ' + str(frequencies))
    return render_template('index.html', frequencies=frequencies)


if __name__ == '__main__':
    setup_logging()
    flask_app.run(debug=env.get_debug(), host='0.0.0.0', port=env.get_web_port())
