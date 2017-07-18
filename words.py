import pprint
from operator import itemgetter
import wordcloud
from database import get_noun_frequencies


def print_frequencies(frequencies):
    frequencies = list(frequencies.items())
    pprint.pprint(sorted(frequencies, key=itemgetter(1)))
    print('%d nouns' % len(frequencies))


def remove_nouns_in_blacklist(nouns, blacklist):
    filtered = {}
    for k, v in nouns.items():
        if k not in blacklist:
            filtered[k] = v
    return filtered


def get_filtered_noun_frequencies(nouns, starting_at, black_list):
    frequencies = get_noun_frequencies(nouns, starting_at)
    return remove_nouns_in_blacklist(frequencies, black_list)


def generate_word_cloud(frequencies, **kwargs):
    return wordcloud.WordCloud(**kwargs).generate_from_frequencies(frequencies).to_image()


def read_black_list():
    with open('blacklist.txt') as f:
        return f.read().split()
