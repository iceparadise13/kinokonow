import unittest
import main


class TestRemoveUrl(unittest.TestCase):
    def test(self):
        expected = 'foo foo'
        self.assertEqual(expected, main.remove_url('foo https://t.co/blahblah foo'))

    def test_greed(self):
        expected = 'foo '
        # `foo` will also be replaced if the regex engine is greedy
        self.assertEqual(expected, main.remove_url('https://t.co/blahblah foo '))


class TestRemoveMention(unittest.TestCase):
    def test(self):
        expected = 'foo foo'
        self.assertEqual(expected, main.remove_mention('foo @blahblah foo'))

    def test_greed(self):
        expected = 'foo '
        self.assertEqual(expected, main.remove_mention('@blahblah foo '))


if __name__ == '__main__':
    unittest.main()
