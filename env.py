import os


def get_debug():
    return True if 'DEBUG' in os.environ else False


def get_ma_host():
    return os.environ.get('MA_HOST', 'localhost')


def get_ma_port():
    return int(os.environ.get('MA_PORT', '5000'))


def get_redis_host():
    return os.environ.get('REDIS_HOST', 'localhost')


def get_redis_port():
    return int(os.environ.get('REDIS_PORT', '6379'))


def get_mongo_host():
    return os.environ.get('MONGO_HOST', 'localhost')


def get_mongo_port():
    return int(os.environ.get('MONGO_PORT', '27017'))


def get_mongo_db():
    return os.environ.get('MONGO_DB', 'db')
