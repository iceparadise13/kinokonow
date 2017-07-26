import unittest
from datetime import datetime, timezone
import mongomock
import database


def create_utc_date(*args, **kwargs):
    return datetime(*args, **kwargs, tzinfo=timezone.utc)


class TestMongo(unittest.TestCase):
    def setUp(self):
        self.db = mongomock.MongoClient().db
        self.old_db = database.db
        database.db = self.db

    def tearDown(self):
        database.db = self.old_db
