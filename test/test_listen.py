import unittest
from kinokonow import listen


class TestExtractSource(unittest.TestCase):
    def test(self):
        source = '<a href="http://twitter.com/download/android" rel="nofollow">Twitter for Android</a> '
        self.assertEqual('Twitter for Android', listen.extract_source(source))

    def test_ignore_invalid(self):
        source = 'foo'
        self.assertEqual('', listen.extract_source(source))


if __name__ == '__main__':
    unittest.main()
