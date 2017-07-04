from datetime import datetime
import csv
import yaml
from twython import TwythonStreamer


class Streamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
            print('%s %s: %s' % (str(datetime.now()), data['user']['screen_name'], data['text']))

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
        for _, user_id, _ in csv.reader(f):
            yield user_id


if __name__ == '__main__':
    users_to_follow = list(get_followers())
    print('following %d users' % len(users_to_follow))
    stream = get_streamer()
    stream.statuses.filter(follow=','.join(users_to_follow))
