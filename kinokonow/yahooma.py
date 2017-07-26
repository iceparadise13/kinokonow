import json
import re
import requests
from flask import Flask, request
from kinokonow import env, settings


flask_app = Flask(__name__, template_folder='templates')


class YahooApi(object):
    def __init__(self, api_key, session=None):
        self.api_key = api_key
        self.session = session or requests.Session()

    def parse(self, text):
        pat = 'https://jlp.yahooapis.jp/MAService/V1/parse?appid=%s&sentence=%s'
        resp = self.session.get(pat % (self.api_key, text))
        # キーフレーズ解析と違ってjsonに対応していない模様
        # 返ってくるxmlをパース出来るいい感じのライブラリが無いので強引に正規表現でやる
        return re.findall('<surface>(.+?)</surface>.+?<pos>(.+?)</pos>', resp.content.decode('utf-8'))


def extract_nouns(tweet):
    """
    与えられたツイートから名詞を抽出する
    :param tweet: ツイート
    :return: 抽出された名詞のリスト
    """
    api = YahooApi(settings.get_yahoo_api_key())
    return [word for word, pos in api.parse(tweet) if pos == '名詞']


@flask_app.route('/')
def home():
    return json.dumps(extract_nouns(request.args.get('tweet')))


if __name__ == '__main__':
    debug = env.get_debug()
    port = env.get_ma_port()
    flask_app.run(debug=debug, host='0.0.0.0', port=port)
