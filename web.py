import pymongo
from flask import Flask, render_template


app = Flask(__name__, template_folder='templates')
client = pymongo.MongoClient(host='localhost', port=27017)
db = client.get_database('kinokonow')


@app.route('/')
def home():
    return render_template('index.html', frequencies=[])


if __name__ == '__main__':
    app.run(debug=True)
