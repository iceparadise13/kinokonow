import json
from flask import Flask, render_template, request
import score
import env
from operator import itemgetter
import database


flask_app = Flask(__name__, template_folder='templates')


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


@flask_app.route('/search', methods=['POST'])
def search():
    query = request.form['search-query']
    return json.dumps(database.search_tweet(query))


@flask_app.route('/', methods=['GET'])
def home():
    cap = 50
    scores = score.score_key_phrases(save=False)
    frequencies = scores_to_frequencies(scores, (1, 10))
    frequencies = sorted(frequencies, key=itemgetter(1), reverse=True)
    print(frequencies)
    return render_template('index.html', frequencies=frequencies[:cap])


if __name__ == '__main__':
    flask_app.run(debug=env.get_debug(), host='0.0.0.0', port=env.get_web_port())
