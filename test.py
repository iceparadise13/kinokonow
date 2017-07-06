import unittest
from unittest import mock
from datetime import datetime
import mongomock
import extract
import words


class TestRemoveUrl(unittest.TestCase):
    def test(self):
        expected = 'foo foo'
        self.assertEqual(expected, extract.remove_url('foo https://t.co/bar foo'))

    def test_eol(self):
        expected = 'foo '
        self.assertEqual(expected, extract.remove_url('foo https://t.co/bar'))

    def test_greed(self):
        expected = 'foo '
        # `foo` will also be replaced if the regex engine is greedy
        self.assertEqual(expected, extract.remove_url('https://t.co/bar foo '))


class TestRemoveMention(unittest.TestCase):
    def test(self):
        expected = 'foo foo'
        self.assertEqual(expected, extract.remove_mention('foo @bar foo'))

    def test_eol(self):
        expected = 'foo '
        self.assertEqual(expected, extract.remove_mention('foo @bar'))

    def test_greed(self):
        expected = 'foo '
        self.assertEqual(expected, extract.remove_mention('@bar foo '))


class TestRemoveRtBoilerplate(unittest.TestCase):
    def test(self):
        expected = 'foo'
        self.assertEqual(expected, extract.remove_rt_boilerplate('RT @bar: foo'))


class TestYahooApi(unittest.TestCase):
    def setUp(self):
        self.session = mock.MagicMock()

    def set_content(self, content):
        self.session.get.return_value = mock.MagicMock(content=content)

    def extract_phrases(self):
        api = extract.YahooApi('foo', self.session)
        self.result = api.extract_phrases('bar baz')

    def test_url_called(self):
        self.set_content(b'{}')
        self.extract_phrases()
        url = 'https://jlp.yahooapis.jp/KeyphraseService/V1/extract?' \
              'appid=foo&output=json&sentence=bar baz'
        self.session.get.assert_called_once_with(url)

    def test_return_nouns(self):
        self.set_content(b'{"bar": 60, "baz": 40}')
        self.extract_phrases()
        self.assertEqual(sorted(['bar', 'baz']), sorted(self.result))

    def test_handle_empty_list(self):
        self.set_content(b'[]')
        self.extract_phrases()
        self.assertEqual([], self.result)

    def test_handle_error(self):
        self.set_content(b'["Error"]')
        self.extract_phrases()
        self.assertEqual([], self.result)


class TestGetNounFrequencies(unittest.TestCase):
    def test_frequency(self):
        collection = mongomock.MongoClient().db.collection
        created_at = datetime(2017, 1, 1, 1, 0, 0)
        collection.insert_many([
            {'text': 'a', 'created_at': created_at},
            {'text': 'b', 'created_at': created_at},
            {'text': 'b', 'created_at': created_at},
        ])
        expected = {'a': 1, 'b': 2}
        result = words.get_noun_frequencies(collection, created_at)
        self.assertEqual(expected, result)

    def test_starting_at(self):
        collection = mongomock.MongoClient().db.collection
        collection.insert_many([
            {'text': 'a', 'created_at': datetime(2017, 1, 1, 1, 0, 0)},
            {'text': 'a', 'created_at': datetime(2017, 1, 1, 1, 0, 1)},
            {'text': 'a', 'created_at': datetime(2017, 1, 1, 1, 0, 1)},
        ])
        expected = {'a': 2}
        result = words.get_noun_frequencies(collection, datetime(2017, 1, 1, 1, 0, 1))
        self.assertEqual(expected, result)


class TestRemoveNounsInBlacklist(unittest.TestCase):
    def test(self):
        frequencies = {
            'a': 1,
            'b': 2,
            'c': 3,
        }
        blacklist = ['a', 'b']
        expected = {'c': 3}
        self.assertEqual(expected, words.remove_nouns_in_blacklist(frequencies, blacklist))


if __name__ == '__main__':
    unittest.main()
