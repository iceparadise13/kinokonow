import pprint
from operator import itemgetter
from datetime import datetime, timedelta
import wordcloud
import pymongo


def print_frequencies(frequencies):
    frequencies = list(frequencies.items())
    pprint.pprint(sorted(frequencies, key=itemgetter(1)))
    print('%d nouns' % len(frequencies))


def get_noun_frequencies(nouns, starting_at):
    cusor = nouns.aggregate([
        {'$match': {'created_at': {'$gte': starting_at}}},
        {'$group': {'_id': '$text', 'frequency': {'$sum': 1}}}
    ])
    return dict([(c['_id'], c['frequency']) for c in cusor])


def remove_nouns_in_blacklist(nouns, blacklist):
    filtered = {}
    for k, v in nouns.items():
        if k not in blacklist:
            filtered[k] = v
    return filtered


def get_filtered_noun_frequencies(nouns, starting_at, black_list):
    frequencies = get_noun_frequencies(nouns, starting_at)
    return remove_nouns_in_blacklist(frequencies, black_list)


if __name__ == '__main__':
    frequencies = {}

    with open('blacklist.txt') as f:
        black_list = f.read().split()

    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client.get_database('kinokonow')

    frequencies = get_filtered_noun_frequencies(db.nouns, datetime.utcnow() - timedelta(hours=1), black_list)
    print_frequencies(frequencies)
    cloud = wordcloud.WordCloud(font_path='font.ttf').generate_from_frequencies(frequencies)
    img = cloud.to_image()
    img.save('out.png')
