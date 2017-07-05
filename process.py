import re
import sys
import json
import requests
import wordcloud


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
    frequencies = {}

    api = YahooApi(sys.argv[1])

    with open('tweets.txt') as f:
        while 1:
            line = f.readline()
            if not line:
                break
            data = json.loads(line)
            text = data['text']
            print(data['user']['screen_name'], ':', data['text'])
            text = clean(text)
            print('cleaned: ' + text)
            nouns = api.extract_phrases(text)
            print('nouns:', nouns)
            for noun in nouns:
                if noun not in frequencies:
                    frequencies[noun] = 0
                frequencies[noun] += 1
            print()
        cloud = wordcloud.WordCloud(font_path='font.ttf').generate_from_frequencies(frequencies)
        img = cloud.to_image()
        img.save('out.png')
