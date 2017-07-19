import unittest
from datetime import datetime, timedelta

import score
import tasks
import tfidf
from test.test_mongo import TestMongo


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
        self.assertNotEqual(0.0, score.score_key_phrases(save=True)['a'])
