import json
from flask import Flask, request
import env
from pyknp import Jumanpp


flask_app = Flask(__name__, template_folder='templates')


def extract_nouns_from_sentence(sentence, analyzer):
    # 改行分けされた複数の文章が渡されても最初の文章しか解析されないため、文章は一つずつ渡す必要がある
    return [anal.midasi for anal in analyzer(sentence) if anal.hinsi == '名詞']


def extract_nouns(tweet, analyzer=None):
    """
    与えられたツイートから名詞を抽出する
    ハッシュタグは無条件で名詞として扱う
    :param data: ツイートとハッシュタグのリストのタプル
    :param analyzer: モック用
    :return: 抽出された名詞のリスト
    """
    analyzer = analyzer or (lambda sentence: Jumanpp().analysis(sentence).mrph_list())
    nouns = []
    for sentence in tweet.split('\n'):
        print('Extracting nouns from %s' % repr(sentence))
        if sentence:
            nouns += extract_nouns_from_sentence(sentence, analyzer)
    return nouns


@flask_app.route('/')
def home():
    return json.dumps(extract_nouns(request.args.get('tweet')))


if __name__ == '__main__':
    flask_app.run(debug=env.get_debug(), host='0.0.0.0', port=env.get_ma_port())
