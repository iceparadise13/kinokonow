import re
import sys
import json
from datetime import datetime
import requests
import redis
import pymongo


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

    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client.get_database('kinokonow')

    while 1:
        result = redis_client.brpop('tweets', timeout=10)
        if not result:
            # the queue was not populated within `timeout` seconds
            continue
        key, value = result
        tweet_data = json.loads(value.decode('utf-8'))
        text = tweet_data['text']
        cleaned_text = clean(text)
        print('screen_name: ', tweet_data['user']['screen_name'])
        print('tweet: ', text)
        print('cleaned_text: ', cleaned_text)
        try:
            nouns = api.extract_phrases(cleaned_text)
            print('nouns :', nouns)
            if nouns:
                db.nouns.insert_many([{'text': n, 'created_at': datetime.utcnow()} for n in nouns])
        except requests.exceptions.RequestException as e:
            print(str(e))
