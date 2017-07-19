import pprint
from operator import itemgetter
import wordcloud


def print_frequencies(frequencies):
    frequencies = list(frequencies.items())
    pprint.pprint(sorted(frequencies, key=itemgetter(1)))
    print('%d nouns' % len(frequencies))


def generate_word_cloud(frequencies, **kwargs):
    return wordcloud.WordCloud(**kwargs).generate_from_frequencies(frequencies).to_image()
