import json
import unittest

import kinokonow.search
from kinokonow import web
from utils import create_utc_date, TestMongo


class TestSearch(TestMongo):
    def setUp(self):
        self.app = web.flask_app.test_client()
        super(TestSearch, self).setUp()

    def test_accessible(self):
        self.assertEqual(200, self.app.get('/').status_code)

    def test_search(self):
        self.db.tweets.insert_one({
            'text': '@foo bar',
            'text_norm': 'bar',
            'user': {'name': 'qux'},
            'created_at': create_utc_date(2017, 1, 1)})
        resp = self.app.post('/search', data={'search-query': 'bar'})
        result = json.loads(resp.data.decode('utf-8'))
        self.assertEqual(1, len(result))
        self.assertEqual([{'user': 'qux', 'text': '@foo bar', 'created_at': 1483228800}], result)

    def test_lower_case(self):
        self.db.tweets.insert_one({
            'text': 'bAr',
            'text_norm': 'bar',
            'user': {'name': 'qux'},
            'created_at': create_utc_date(2017, 1, 1)})
        resp = self.app.post('/search', data={'search-query': 'bAR'})
        result = json.loads(resp.data.decode('utf-8'))
        self.assertEqual(1, len(result))
        self.assertEqual('bAr', result[0]['text'])


class TestNormalizeQuery(TestMongo):
    def test(self):
        self.assertEqual('bar', kinokonow.search.normalize_search_query('BAR'))


class TestPrepareSearchResults(TestMongo):
    def test(self):
        data = {'text': 'foo bar baz', 'user': {'name': 'bob'},
                'created_at': create_utc_date(2017, 1, 1, 0, 0, 0)}
        expected = [{'text': 'foo bar baz', 'user': 'bob', 'created_at': 1483228800}]
        self.assertEqual(expected, web.prepare_search_results([data], 100))


if __name__ == '__main__':
    unittest.main()
