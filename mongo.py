import pymongo
import env


def connect():
    client = pymongo.MongoClient(host=env.get_mongo_host(), port=env.get_mongo_port())
    return client.get_database(env.get_mongo_db())
