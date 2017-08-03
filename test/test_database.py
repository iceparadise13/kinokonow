import json
import unittest
from datetime import datetime, timedelta

import kinokonow.search
from kinokonow import database
from utils import create_utc_date, TestMongo


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


class TestSavePhrases(TestMongo):
    def test(self):
        phrasess = ['a', 'b']
        database.save_phrases(phrasess)
        saved_phrases = list(self.db.phrases.find())
        self.assertEqual('a', saved_phrases[0]['text'])
        self.assertEqual('b', saved_phrases[1]['text'])
        # assert created_at is close enough
        for i in range(len(phrasess)):
            self.assertLess(saved_phrases[i]['created_at'] - datetime.utcnow(), timedelta(seconds=5))


class ConvertTweetTime(unittest.TestCase):
    def test_timezone_converted(self):
        expected = create_utc_date(year=2017, month=1, day=1, hour=1, minute=1, second=1)
        self.assertEqual(expected, database.convert_tweet_date('Fri Jan 01 10:01:01 +0900 2017'))


class TestNormalizeTweet(unittest.TestCase):
    @staticmethod
    def normalize(tweet):
        return kinokonow.search.normalize_tweet(tweet)

    def test_remove_mention(self):
        self.assertEqual('bar', self.normalize('@foo bar'))

    def test_remove_url(self):
        self.assertEqual('bar', self.normalize('https://t.co/foo bar'))
        self.assertEqual('bar ', self.normalize('bar https://t.co/foo'))

    def test_remove_rt_boiler_plate(self):
        self.assertEqual('bar', self.normalize('RT @foo: bar'))

    def test_lower_case(self):
        self.assertEqual('barあ', self.normalize('BARあ'))


class TestSaveTweet(TestMongo):
    def setUp(self):
        self.data = {
            'id_str': 'tweet_id',
            'user': {'name': 'bob',
                     'id_str': '123456',
                     'screen_name': 'realBob',
                     'profile_image_url_https': 'https://a.com'},
            'text': '@foo bar',
            'text_norm': 'bar',
            'source': '<a>Twitter for iPhone</a>',
            'favorite_count': 1,
            'retweet_count': 2,
            'created_at': 'Fri Jul 07 11:35:39 +0000 2017'}
        super(TestSaveTweet, self).setUp()

    def test_data_saved(self):
        database.save_tweet(self.data)
        t = self.db.tweets.find()[0]
        self.assertEqual('tweet_id', t['id'])
        self.assertEqual('@foo bar', t['text'])
        self.assertEqual('bar', t['text_norm'])
        self.assertEqual('bob', t['user']['name'])
        self.assertEqual('123456', t['user']['id'])
        self.assertEqual('realBob', t['user']['screen_name'])
        self.assertEqual('https://a.com', t['user']['profile_image_url'])
        self.assertEqual('<a>Twitter for iPhone</a>', t['source'])
        self.assertEqual(1, t['favorite_count'])
        self.assertEqual(2, t['retweet_count'])
        expected = create_utc_date(year=2017, month=7, day=7, hour=11, minute=35, second=39)
        self.assertEqual(expected, t['created_at'])

    def test_unnecessary_data_removed(self):
        self.data['garbage'] = 'data'
        database.save_tweet(self.data)
        self.assertNotIn('garbage', self.db.tweets.find()[0])


class TestGetPhraseFrequencies(TestMongo):
    def test_frequency(self):
        created_at = datetime(2017, 1, 1, 1, 0, 0)
        self.db.phrases.insert_many([
            {'text': 'a', 'created_at': created_at},
            {'text': 'b', 'created_at': created_at},
            {'text': 'b', 'created_at': created_at},
        ])
        expected = {'a': 1, 'b': 2}
        result = database.get_phrase_frequencies(created_at)
        self.assertEqual(expected, result)

    def test_starting_at(self):
        self.db.phrases.insert_many([
            {'text': 'a', 'created_at': datetime(2017, 1, 1, 1, 0, 0)},
            {'text': 'a', 'created_at': datetime(2017, 1, 1, 1, 0, 1)},
            {'text': 'a', 'created_at': datetime(2017, 1, 1, 1, 0, 1)},
        ])
        expected = {'a': 2}
        result = database.get_phrase_frequencies(datetime(2017, 1, 1, 1, 0, 1))
        self.assertEqual(expected, result)


class TestSearch(TestMongo):
    def search(self, query):
        return list(database.search_tweet(query))

    def test(self):
        data_1 = {'text_norm': 'foo bar baz'}
        data_2 = {'text_norm': 'qux quux corge'}
        self.db.tweets.insert_many([data_1, data_2])
        result = self.search('bar')
        self.assertEqual(1, len(result))
        self.assertEqual('foo bar baz', result[0]['text_norm'])

    def test_sort_by_date(self):
        data_1 = {'text_norm': 'foo', 'created_at': create_utc_date(2017, 1, 1)}
        data_2 = {'text_norm': 'foo bar', 'created_at': create_utc_date(2017, 1, 2)}
        self.db.tweets.insert_many([data_1, data_2])
        self.assertEqual(['foo bar', 'foo'], [d['text_norm'] for d in self.search('foo')])

