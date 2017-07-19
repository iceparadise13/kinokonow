import json
from datetime import datetime, timezone
import pymongo
import env


def connect():
    # `connect`をFalse指定すると最初のクエリで接続するのでプロセスフォークに対応出来る
    client = pymongo.MongoClient(host=env.get_mongo_host(), port=env.get_mongo_port(), connect=False)
    return client.get_database(env.get_mongo_db())


db = connect()


def convert_tweet_date(tweet_date):
    """Convert str datetime provided by twitter api to utc datetime object"""
    dt = datetime.strptime(tweet_date, '%a %b %d %H:%M:%S %z %Y')
    return (dt - dt.utcoffset()).replace(tzinfo=timezone.utc)


def save_nouns(nouns):
    db.nouns.insert_many([{'text': n, 'created_at': datetime.utcnow()} for n in nouns])


def get_documents(since):
    cursor = db.tfidf_documents.find({'created_at': {'$gte': since}})
    return list([json.loads(c['document']) for c in cursor])


def save_document(document, created_at):
    """ドキュメントの単語にピリオドが含まれているとエラーが吐かれるのでjsonとして保管する"""
    return db.tfidf_documents.insert_one({'document': json.dumps(document), 'created_at': created_at})


def get_noun_frequencies(starting_at):
    cursor = db.nouns.aggregate([
        {'$match': {'created_at': {'$gte': starting_at}}},
        {'$group': {'_id': '$text', 'frequency': {'$sum': 1}}}
    ])
    return dict([(c['_id'], c['frequency']) for c in cursor])


def save_tweet(data):
    # shallow copy suffices
    data = dict(data)
    data['created_at'] = convert_tweet_date(data['created_at'])
    db.tweets.insert_one(data)
