import csv
from datetime import datetime, timezone
import yaml
from twython import TwythonStreamer
import tasks
import mongo


settings = yaml.load(open('settings.yml'))
db = mongo.connect(settings['mongo'])


def convert_tweet_date(tweet_date):
    """Convert str datetime provided by twitter api to utc datetime object"""
    dt = datetime.strptime(tweet_date, '%a %b %d %H:%M:%S %z %Y')
    return (dt - dt.utcoffset()).replace(tzinfo=timezone.utc)


def save_tweet(data):
    # shallow copy suffices
    data = dict(data)
    data['created_at'] = convert_tweet_date(data['created_at'])
    db.tweets.insert_one(data)


class Streamer(TwythonStreamer):
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
    yahoo_api_key = open('yahoo_api_key').read()
    users_to_follow = get_followers()
    print('following %d users' % len(users_to_follow))

    def on_success(data):
        if 'text' in data:
            print(data['user']['screen_name'], ':', data['text'], '\n')
            save_tweet(data)
            tasks.create_noun_extraction_task(yahoo_api_key, data['text']).delay()

    stream = get_streamer()
    stream.on_success = on_success
    stream.statuses.filter(follow=','.join(users_to_follow))
