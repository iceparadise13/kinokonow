import re
import sys
import json
import requests


def remove_pattern(pat, text):
    return re.sub('%s(?:\s|$)' % pat, '', text)


def remove_mention(text):
    return remove_pattern('@.+?', text)


def remove_url(text):
    return remove_pattern('(?:http|https)://.+?', text)


def remove_rt_boilerplate(text):
    return remove_pattern('RT @.+:', text)


def clean(text):
    text = remove_rt_boilerplate(text)
    text = remove_url(text)
    return remove_mention(text)


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


if __name__ == '__main__':
    api = YahooApi(sys.argv[1])

    with open('tweets.txt', 'r') as in_file:
        with open('nouns.txt', 'w') as out_file:
            while 1:
                line = in_file.readline()
                if not line:
                    break
                data = json.loads(line)
                text = data['text']
                cleaned_text = clean(text)
                result = {
                    'screen_name': data['user']['screen_name'],
                    'tweet': text,
                    'cleaned_tweet': cleaned_text,
                    'nouns': api.extract_phrases(cleaned_text),
                }
                out_file.write(json.dumps(result) + '\n')
