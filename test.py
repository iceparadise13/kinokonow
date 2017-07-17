import unittest
from unittest import mock
from datetime import datetime, timezone
import mongomock
import tasks
import words
import listen
import jumanpp


class TestPreprocessTweet(unittest.TestCase):
    def test_remove_rt_boilerplate(self):
        tweet = 'RT @bar: foo'
        self.assertEqual('foo', tasks.preprocess_tweet(tweet)[0])

    def test_remove_mention(self):
        self.assertEqual('foobaz', tasks.preprocess_tweet('foo @bar baz ')[0])
        # multiple mentions
        self.assertEqual('foobaz', tasks.preprocess_tweet('foo @bar @bar baz ')[0])
        # eol
        self.assertEqual('foo', tasks.preprocess_tweet('foo @bar')[0])
        # mention only
        self.assertEqual('', tasks.preprocess_tweet('@bar')[0])

    def test_remove_url(self):
        self.assertEqual('foobar', tasks.preprocess_tweet('foo https://t.co/bar bar')[0])
        # multiple urls
        self.assertEqual('foobar', tasks.preprocess_tweet('foo https://t.co/bar https://t.co/bar bar')[0])
        # eol
        self.assertEqual('foo', tasks.preprocess_tweet('foo https://t.co/bar')[0])
        # url only
        self.assertEqual('', tasks.preprocess_tweet('https://t.co/bar')[0])

    def test_remove_spaces(self):
        self.assertEqual('foobarbaz', tasks.preprocess_tweet('foo bar baz ')[0])

    def test_extract_hash_tags(self):
        self.assertEqual(('fooqux', ['bar', 'baz'],), tasks.preprocess_tweet('foo #bar #baz qux'))


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


class ConvertTweetTime(unittest.TestCase):
    def test_date_time_converted(self):
        expected = datetime(year=2017, month=7, day=7, hour=11, minute=35, second=39, tzinfo=timezone.utc)
        self.assertEqual(expected, listen.convert_tweet_date('Fri Jul 07 11:35:39 +0000 2017'))

    def test_timezone_converted(self):
        expected = datetime(year=2017, month=1, day=1, hour=1, minute=1, second=1, tzinfo=timezone.utc)
        self.assertEqual(expected, listen.convert_tweet_date('Fri Jan 01 10:01:01 +0900 2017'))


class TestExtractNouns(unittest.TestCase):
    def test_only_return_nouns(self):
        corpus = '猫を踏んだ'
        analyzer = mock.MagicMock(side_effect=[[
            mock.MagicMock(midasi='猫', hinsi='名詞'),
            mock.MagicMock(midasi='を', hinsi='助詞'),
            mock.MagicMock(midasi='踏んだ', hinsi='動詞')
        ]])
        self.assertEqual(['猫'], jumanpp.extract_nouns(corpus, analyzer))

    def test_multiple_sentences(self):
        corpus = '1\n2\n3'
        analyzer = mock.MagicMock(side_effect=[
            [mock.MagicMock(midasi='1', hinsi='名詞')],
            [mock.MagicMock(midasi='2', hinsi='名詞')],
            [mock.MagicMock(midasi='3', hinsi='名詞')]
        ])
        self.assertEqual(['1', '2', '3'], jumanpp.extract_nouns(corpus, analyzer))
        analyzer.assert_has_calls(
            [mock.call('1'), mock.call('2'), mock.call('3')],
            any_order=True)

    def test_ignore_empty_sentence(self):
        corpus = '\n\n'
        analyzer = mock.MagicMock()
        jumanpp.extract_nouns(corpus, analyzer)
        analyzer.assert_not_called()


if __name__ == '__main__':
    unittest.main()
