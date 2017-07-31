import unittest
from kinokonow import listen


class TestExtractSource(unittest.TestCase):
    def test(self):
        source = '<a href="http://twitter.com/download/android" rel="nofollow">Twitter for Android</a> '
        self.assertEqual('Twitter for Android', listen.extract_source(source))

    def test_ignore_invalid(self):
        source = 'foo'
        self.assertEqual('', listen.extract_source(source))


class TestIsRt(unittest.TestCase):
    def test_true(self):
        self.assertTrue(listen.is_rt('RT foo'))

    def test_false(self):
        self.assertTrue(listen.is_rt('foo'))


if __name__ == '__main__':
    unittest.main()
