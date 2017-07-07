import pymongo
from datetime import datetime, timedelta
from flask import Flask, render_template
import words


app = Flask(__name__, template_folder='templates')
client = pymongo.MongoClient(host='localhost', port=27017)
db = client.get_database('kinokonow')


@app.route('/')
def home():
    frequencies = words.get_filtered_noun_frequencies(
        db.nouns, datetime.utcnow() - timedelta(hours=1), words.read_black_list())
    return render_template('index.html', frequencies=[[k, v] for k, v in frequencies.items()])


if __name__ == '__main__':
    app.run()
