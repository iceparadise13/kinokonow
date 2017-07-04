import re
from datetime import datetime
import csv
import yaml
from twython import TwythonStreamer
import MeCab


def extract_nouns(text):
    mecab = MeCab.Tagger('-Ochasen')
    parsed = mecab.parse(text)
    nouns = []
    for chunk in parsed.splitlines()[:-1]:
        split = chunk.split('\t')
        if split[3].startswith('名詞'):
            nouns.append(split[0])
    return nouns


def remove_mention(text):
    return re.sub('@.+?\s', '', text)


def remove_url(text):
    return re.sub('(?:http|https)://.+?\s', '', text)


class Streamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
            print('%s %s: %s' % (str(datetime.now()), data['user']['screen_name'], data['text']))
            text = data['text']
            text = remove_url(text)
            text = remove_mention(text)
            print(extract_nouns(text))

    def on_error(self, status_code, data):
        print(status_code)
        self.disconnect()


def get_streamer():
    cfg = yaml.load(open('twitter.yml', 'rb'))
    return Streamer(
        cfg['consumer_key'],
        cfg['consumer_secret'],
        cfg['access_token_key'],
        cfg['access_token_secret'])


def get_followers():
    with open('follow.txt') as f:
        return [user_id for _, user_id, _ in csv.reader(f)]


if __name__ == '__main__':
    users_to_follow = get_followers()
    print('following %d users' % len(users_to_follow))
    stream = get_streamer()
    stream.statuses.filter(follow=','.join(users_to_follow))
