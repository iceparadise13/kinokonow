import unittest
from datetime import datetime, timedelta

import tasks
import tfidf
import words
from test.test_mongo import TestMongo


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


class TestScoreTfIdf(unittest.TestCase):
    def test_reward_frequent_words_in_document(self):
        document = {'foo': 1, 'bar': 2}
        past_documents = [{}]
        scores = tfidf.score(document, past_documents)
        self.assertGreater(scores['bar'], scores['foo'])

    def test_punish_frequent_words_across_all_documents(self):
        document = {'foo': 1, 'bar': 2}
        past_documents = [{'bar': 1}, {'bar': 1}]
        scores = tfidf.score(document, past_documents)
        self.assertGreater(scores['foo'], scores['bar'])

    def test_scale_punishment_for_excessively_frequent_words(self):
        document = {'foo': 1, 'bar': 10}
        past_documents = [{'bar': 1}] * 10
        # Add garbage to ensure that there are more documents than
        # the number of documents containing "bar" so that x of log(x) is greater than 1
        past_documents += [{'baz': 1}] * 10
        scores = tfidf.score(document, past_documents)
        self.assertGreater(scores['foo'], scores['bar'])


class TestTfIdf(unittest.TestCase):
    def test_bypass_zero_division(self):
        t = tfidf.TfIdf([{'foo': 1}])
        self.assertEqual(1, t._idf('bar'))


class TestInitialTfIdfDocument(TestMongo):
    def test_initial_tfidf_document_scored_properly(self):
        thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)
        self.db.nouns.insert_many([{'text': 'a', 'created_at': thirty_minutes_ago}])
        self.assertNotEqual(0.0, tasks.score_key_phrases()['a'])


if __name__ == '__main__':
    unittest.main()
