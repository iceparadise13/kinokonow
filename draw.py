import wordcloud
from util import iterate_json


if __name__ == '__main__':
    frequencies = {}

    with open('blacklist.txt') as f:
        black_list = f.read().split()

    with open('nouns.txt') as f:
        for line in iterate_json(f):
            for n in line['nouns']:
                if n in black_list:
                    continue
                if n not in frequencies:
                    frequencies[n] = 0
                frequencies[n] += 1

    cloud = wordcloud.WordCloud(font_path='font.ttf').generate_from_frequencies(frequencies)
    img = cloud.to_image()
    img.save('out.png')
