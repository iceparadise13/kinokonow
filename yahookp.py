import os
import json
import requests
from flask import Flask, request
from util import load_yaml


flask_app = Flask(__name__, template_folder='templates')


class YahooApi(object):
    def __init__(self, api_key, session=None):
        self.api_key = api_key
        self.session = session or requests.Session()

    def extract_phrases(self, text):
        pat = 'https://jlp.yahooapis.jp/KeyphraseService/V1/extract?appid=%s&output=json&sentence=%s'
        resp = self.session.get(pat % (self.api_key, text))
        result = json.loads(resp.content.decode('utf-8'))
        if type(result) == dict:
            return list(result.keys())
        return []


def extract_nouns(tweet):
    """
    与えられたツイートから名詞を抽出する
    ハッシュタグは無条件で名詞として扱う
    :param tweet: ツイート
    :return: 抽出された名詞のリスト
    """
    settings = load_yaml('settings.yml')
    api = YahooApi(settings['yahoo_api_key'])
    return api.extract_phrases(tweet)


@flask_app.route('/')
def home():
    return json.dumps(extract_nouns(request.args.get('tweet')))


if __name__ == '__main__':
    debug = True if 'DEBUG' in os.environ else False
    port = int(os.environ.get('MA_PORT', '5000'))
    flask_app.run(debug=debug, host='0.0.0.0', port=port)
