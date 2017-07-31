import unittest
from kinokonow import filter


class TestPreMa(unittest.TestCase):
    def test_remove_rt_boilerplate(self):
        tweet = 'RT @bar: foo'
        self.assertEqual('foo', filter.pre_ma(tweet)[0])

    def test_remove_mention(self):
        self.assertEqual('foo baz ', filter.pre_ma('foo @bar baz ')[0])
        # multiple mentions
        self.assertEqual('foo baz ', filter.pre_ma('foo @bar @bar baz ')[0])
        # eol
        self.assertEqual('foo ', filter.pre_ma('foo @bar')[0])
        # mention only
        self.assertEqual('', filter.pre_ma('@bar')[0])

    def test_remove_url(self):
        self.assertEqual('foo bar', filter.pre_ma('foo https://t.co/bar bar')[0])
        # multiple urls
        self.assertEqual('foo bar', filter.pre_ma('foo https://t.co/bar https://t.co/bar bar')[0])
        # eol
        self.assertEqual('foo ', filter.pre_ma('foo https://t.co/bar')[0])
        # url only
        self.assertEqual('', filter.pre_ma('https://t.co/bar')[0])

    def test_extract_hash_tags(self):
        self.assertEqual(('foo   qux', ['bar', 'baz'],), filter.pre_ma('foo #bar #baz qux'))


if __name__ == '__main__':
    unittest.main()
