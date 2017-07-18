import unittest
import json
from datetime import datetime, timezone
import mongomock
import database
import tasks
import words
import listen
import tfidf


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
        result = database.get_noun_frequencies(collection, created_at)
        self.assertEqual(expected, result)

    def test_starting_at(self):
        collection = mongomock.MongoClient().db.collection
        collection.insert_many([
            {'text': 'a', 'created_at': datetime(2017, 1, 1, 1, 0, 0)},
            {'text': 'a', 'created_at': datetime(2017, 1, 1, 1, 0, 1)},
            {'text': 'a', 'created_at': datetime(2017, 1, 1, 1, 0, 1)},
        ])
        expected = {'a': 2}
        result = database.get_noun_frequencies(collection, datetime(2017, 1, 1, 1, 0, 1))
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


class TestGetDocuments(unittest.TestCase):
    def test(self):
        collection = mongomock.MongoClient().db.collection
        subdoc_1 = {'foo': 1}
        subdoc_2 = {'bar': 2}
        doc_1 = {'_id': 1, 'document': json.dumps(subdoc_1), 'created_at': datetime(year=2017, month=1, day=1, tzinfo=timezone.utc)}
        doc_2 = {'_id': 2, 'document': json.dumps(subdoc_2), 'created_at': datetime(year=2017, month=1, day=2, tzinfo=timezone.utc)}
        collection.insert_many([doc_1, doc_2])
        result = database.get_documents(collection, datetime(year=2017, month=1, day=2, tzinfo=timezone.utc))
        self.assertEqual([subdoc_2], result)


class TestSaveDocument(unittest.TestCase):
    def test_document_is_saved_as_json(self):
        collection = mongomock.MongoClient().db.collection
        document = {'.': 1}
        created_at = datetime(year=2017, month=1, day=1, tzinfo=timezone.utc)
        database.save_document(collection, document, created_at)
        self.assertTrue(collection.find({'document': json.dumps(document)}).count())


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


if __name__ == '__main__':
    unittest.main()
