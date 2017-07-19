import json
import unittest
from datetime import datetime, timezone, timedelta

import database
from test.test_mongo import TestMongo


def create_utc_date(*args, **kwargs):
    return datetime(*args, **kwargs, tzinfo=timezone.utc)


class TestGetDocuments(TestMongo):
    def test(self):
        subdoc_1 = {'foo': 1}
        subdoc_2 = {'bar': 2}
        doc_1 = {'document': json.dumps(subdoc_1),
                 'created_at': create_utc_date(year=2017, month=1, day=1)}
        doc_2 = {'document': json.dumps(subdoc_2),
                 'created_at': create_utc_date(year=2017, month=1, day=2)}
        self.db.tfidf_documents.insert_many([doc_1, doc_2])
        result = database.get_documents(create_utc_date(year=2017, month=1, day=2))
        self.assertEqual([subdoc_2], result)


class TestSaveDocument(TestMongo):
    def test_document_is_saved_as_json(self):
        document = {'.': 1}
        created_at = create_utc_date(year=2017, month=1, day=1)
        database.save_document(document, created_at)
        self.assertTrue(self.db.tfidf_documents.find({'document': json.dumps(document)}).count())


class TestSaveNouns(TestMongo):
    def test(self):
        nouns = ['a', 'b']
        database.save_nouns(nouns)
        saved_nouns = list(self.db.nouns.find())
        self.assertEqual('a', saved_nouns[0]['text'])
        self.assertEqual('b', saved_nouns[1]['text'])
        # assert created_at is close enough
        for i in range(len(nouns)):
            self.assertLess(saved_nouns[i]['created_at'] - datetime.utcnow(), timedelta(seconds=5))


class ConvertTweetTime(unittest.TestCase):
    def test_timezone_converted(self):
        expected = create_utc_date(year=2017, month=1, day=1, hour=1, minute=1, second=1)
        self.assertEqual(expected, database.convert_tweet_date('Fri Jan 01 10:01:01 +0900 2017'))


class TestSaveTweet(TestMongo):
    def test_datetime_converted(self):
        expected = create_utc_date(year=2017, month=7, day=7, hour=11, minute=35, second=39)
        data = {'created_at': 'Fri Jul 07 11:35:39 +0000 2017', 'text': 'foo'}
        database.save_tweet(data)
        self.assertEqual(expected, self.db.tweets.find()[0]['created_at'])


class TestGetNounFrequencies(TestMongo):
    def test_frequency(self):
        created_at = datetime(2017, 1, 1, 1, 0, 0)
        self.db.nouns.insert_many([
            {'text': 'a', 'created_at': created_at},
            {'text': 'b', 'created_at': created_at},
            {'text': 'b', 'created_at': created_at},
        ])
        expected = {'a': 1, 'b': 2}
        result = database.get_noun_frequencies(created_at)
        self.assertEqual(expected, result)

    def test_starting_at(self):
        self.db.nouns.insert_many([
            {'text': 'a', 'created_at': datetime(2017, 1, 1, 1, 0, 0)},
            {'text': 'a', 'created_at': datetime(2017, 1, 1, 1, 0, 1)},
            {'text': 'a', 'created_at': datetime(2017, 1, 1, 1, 0, 1)},
        ])
        expected = {'a': 2}
        result = database.get_noun_frequencies(datetime(2017, 1, 1, 1, 0, 1))
        self.assertEqual(expected, result)
