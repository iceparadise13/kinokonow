import pymongo


def connect(settings):
    client = pymongo.MongoClient(host=settings['host'], port=settings['port'])
    return client.get_database(settings['db'])
