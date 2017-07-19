import unittest

import tasks
import words


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


if __name__ == '__main__':
    unittest.main()
