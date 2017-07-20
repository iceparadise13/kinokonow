import unittest
import json
from operator import itemgetter
import web
from test_mongo import TestMongo


class TestScoresToFrequencies(unittest.TestCase):
    def sort(self, inp):
        return sorted(inp, key=itemgetter(1, 0))

    def test(self):
        scores = {'foo': 0.05, 'bar': 0.10, 'baz': 0.15}
        expected = [['foo', 1], ['bar', 10], ['baz', 20]]
        result = web.scores_to_frequencies(scores, (1, 20))
        self.assertEqual(self.sort(expected), self.sort(result))

    def test_empty_sequence(self):
        self.assertEqual([], web.scores_to_frequencies({}, None))

    def test_bypass_division_by_zero(self):
        scores = {'foo': 1, 'bar': 1}
        expected = [['foo', 10], ['bar', 10]]
        result = web.scores_to_frequencies(scores, (1, 20))
        self.assertEqual(self.sort(expected), self.sort(result))


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
