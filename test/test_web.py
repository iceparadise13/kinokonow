import unittest
from operator import itemgetter
import web


class TestScoresToFrequencies(unittest.TestCase):
    def sort(self, inp):
        return sorted(inp, key=itemgetter(1))

    def test(self):
        scores = {'foo': 0.05, 'bar': 0.10, 'baz': 0.15}
        expected = [['foo', 1], ['bar', 10], ['baz', 20]]
        result = web.scores_to_frequencies(scores, (1, 20))
        self.assertEqual(self.sort(expected), self.sort(result))


if __name__ == '__main__':
    unittest.main()
