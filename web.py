from datetime import datetime, timedelta
from operator import itemgetter
import pymongo
from flask import Flask, render_template
import words


flask_app = Flask(__name__, template_folder='templates')
client = pymongo.MongoClient(host='localhost', port=27017)
db = client.get_database('kinokonow')


@flask_app.route('/')
def home():
    frequencies = words.get_filtered_noun_frequencies(
        db.nouns, datetime.utcnow() - timedelta(hours=1), words.read_black_list())
    frequencies = [[k, v] for k, v in frequencies.items()]
    frequencies = sorted(frequencies, key=itemgetter(1), reverse=True)[:50]
    return render_template('index.html', frequencies=frequencies)


if __name__ == '__main__':
    flask_app.run(debug=True, host='0.0.0.0')
