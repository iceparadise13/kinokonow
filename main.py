from datetime import datetime
import yaml
from twython import TwythonStreamer


class Streamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
            print('%s %s: %s' % (str(datetime.now()), data['user']['screen_name'], data['text'].encode('utf-8')))

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


if __name__ == '__main__':
    users_to_follow = open('follow.txt').read().strip()
    print('following %d users' % len(users_to_follow.split(',')))
    stream = get_streamer()
    stream.statuses.filter(follow=users_to_follow)
