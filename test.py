import unittest
import main


class TestRemoveUrl(unittest.TestCase):
    def test(self):
        expected = 'foo foo'
        self.assertEqual(expected, main.remove_url('foo https://t.co/bar foo'))

    def test_eol(self):
        expected = 'foo '
        self.assertEqual(expected, main.remove_url('foo https://t.co/bar'))

    def test_greed(self):
        expected = 'foo '
        # `foo` will also be replaced if the regex engine is greedy
        self.assertEqual(expected, main.remove_url('https://t.co/bar foo '))


class TestRemoveMention(unittest.TestCase):
    def test(self):
        expected = 'foo foo'
        self.assertEqual(expected, main.remove_mention('foo @bar foo'))

    def test_eol(self):
        expected = 'foo '
        self.assertEqual(expected, main.remove_mention('foo @bar'))

    def test_greed(self):
        expected = 'foo '
        self.assertEqual(expected, main.remove_mention('@bar foo '))


class TestRemoveRtBoilerplate(unittest.TestCase):
    def test(self):
        expected = 'foo'
        self.assertEqual(expected, main.remove_rt_boilerplate('RT @bar: foo'))


if __name__ == '__main__':
    unittest.main()
