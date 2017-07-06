import pprint
from operator import itemgetter
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


if __name__ == '__main__':
    frequencies = {}

    with open('blacklist.txt') as f:
        black_list = f.read().split()

    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client.get_database('kinokonow')
    frequencies = get_noun_frequencies(db.nouns)

    print_frequencies(frequencies)

    cloud = wordcloud.WordCloud(font_path='font.ttf').generate_from_frequencies(frequencies)
    img = cloud.to_image()
    img.save('out.png')
