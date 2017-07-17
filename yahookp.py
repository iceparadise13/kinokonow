import json
import requests
from flask import Flask, request
import settings
import env


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
    api = YahooApi(settings.get_yahoo_api_key())
    return api.extract_phrases(tweet)


@flask_app.route('/')
def home():
    return json.dumps(extract_nouns(request.args.get('tweet')))


if __name__ == '__main__':
    debug = env.get_debug()
    port = env.get_ma_port()
    flask_app.run(debug=debug, host='0.0.0.0', port=port)
