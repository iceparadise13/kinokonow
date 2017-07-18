import json


def get_documents(collection, since):
    cursor = collection.find({'created_at': {'$gte': since}})
    return list([json.loads(c['document']) for c in cursor])


def save_document(collection, document, created_at):
    """ドキュメントの単語にピリオドが含まれているとエラーが吐かれるのでjsonとして保管する"""
    return collection.insert_one({'document': json.dumps(document), 'created_at': created_at})


def get_noun_frequencies(nouns, starting_at):
    cursor = nouns.aggregate([
        {'$match': {'created_at': {'$gte': starting_at}}},
        {'$group': {'_id': '$text', 'frequency': {'$sum': 1}}}
    ])
    return dict([(c['_id'], c['frequency']) for c in cursor])
