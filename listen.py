import csv
from datetime import datetime, timezone
from twython import TwythonStreamer
import tasks
import mongo
from util import load_yaml


def convert_tweet_date(tweet_date):
    """Convert str datetime provided by twitter api to utc datetime object"""
    dt = datetime.strptime(tweet_date, '%a %b %d %H:%M:%S %z %Y')
    return (dt - dt.utcoffset()).replace(tzinfo=timezone.utc)


def save_tweet(db, data):
    # shallow copy suffices
    data = dict(data)
    data['created_at'] = convert_tweet_date(data['created_at'])
    db.tweets.insert_one(data)


class Streamer(TwythonStreamer):
    def on_error(self, status_code, data):
        print(status_code)
        self.disconnect()


def get_streamer(settings):
    return Streamer(
        settings['consumer_key'],
        settings['consumer_secret'],
        settings['access_token_key'],
        settings['access_token_secret'])


def get_followers():
    with open('follow.txt') as f:
        return [user_id for _, user_id, _ in csv.reader(f)]


if __name__ == '__main__':
    settings = load_yaml('settings.yml')
    db = mongo.connect()

    users_to_follow = get_followers()
    print('following %d users' % len(users_to_follow))

    def on_success(data):
        if 'text' in data:
            print(data['user']['screen_name'], ':', data['text'], '\n')
            save_tweet(db, data)
            tasks.create_noun_extraction_task(data['text']).delay()

    stream = get_streamer(settings['twitter'])
    stream.on_success = on_success
    stream.statuses.filter(follow=','.join(users_to_follow))
