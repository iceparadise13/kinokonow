import json
import csv
import yaml
import redis
import pymongo
from twython import TwythonStreamer


redis = redis.StrictRedis(host='localhost', port=6379, db=0)
client = pymongo.MongoClient(host='localhost', port=27017)
db = client.kinokonow


class Streamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
            print(data['user']['screen_name'], ':', data['text'], '\n')
            redis.lpush('tweets', json.dumps(data))
            # this call seems to modify `data` making it impossible to json serialize
            # should be executed after the above
            db.tweets.insert_one(data)

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
