from flask import Flask, render_template
import score
import env
from operator import itemgetter


flask_app = Flask(__name__, template_folder='templates')


def scores_to_frequencies(scores, freq_range):
    min_score = min(scores.values())
    max_score = max(scores.values())
    result = []
    for k, v in scores.items():
        fraction = (v - min_score) / (max_score - min_score)
        v = freq_range[0] + ((freq_range[1] - freq_range[0]) * fraction)
        result.append([k, int(v)])
    return result


@flask_app.route('/')
def home():
    cap = 50
    scores = score.score_key_phrases(save=False)
    frequencies = scores_to_frequencies(scores, (1, 10))
    frequencies = sorted(frequencies, key=itemgetter(1), reverse=True)
    print(frequencies)
    return render_template('index.html', frequencies=frequencies[:cap])


if __name__ == '__main__':
    flask_app.run(debug=env.get_debug(), host='0.0.0.0', port=env.get_web_port())
