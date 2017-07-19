import pymongo
from flask import Flask, render_template
import random


flask_app = Flask(__name__, template_folder='templates')
client = pymongo.MongoClient(host='localhost', port=27017)
db = client.get_database('kinokonow')


@flask_app.route('/')
def home():
    frequencies = []
    for i in range(50):
        frequencies.append([''.join(random.sample(['a', 'b', 'c'], random.randint(1, 3))), random.randint(1, 20)])
    return render_template('index.html', frequencies=frequencies)


if __name__ == '__main__':
    flask_app.run(debug=True, host='0.0.0.0')
