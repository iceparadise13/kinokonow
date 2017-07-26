import unittest
import json
from operator import itemgetter
import web
from test_mongo import TestMongo


class TestSearch(TestMongo):
    def setUp(self):
        self.app = web.flask_app.test_client()
        super(TestSearch, self).setUp()

    def test_accessible(self):
        self.assertEqual(200, self.app.get('/').status_code)

    def test_search(self):
        self.db.tweets.insert_one({'text': 'foo bar baz', 'user': {'name': 'qux'}})
        resp = self.app.post('/search', data={'search-query': 'bar'})
        self.assertEqual([{'user': 'qux', 'text': 'foo bar baz'}], json.loads(resp.data.decode('utf-8')))


if __name__ == '__main__':
    unittest.main()
