import unittest
import mongomock
import database


class TestMongo(unittest.TestCase):
    def setUp(self):
        self.db = mongomock.MongoClient().db
        self.old_db = database.db
        database.db = self.db

    def tearDown(self):
        database.db = self.old_db
