import json
import wordcloud


def iterate_lines(f):
    while 1:
        line = f.readline()
        if not line:
            break
        yield line


if __name__ == '__main__':
    frequencies = {}

    with open('nouns.txt') as f:
        for line in iterate_lines(f):
            data = json.loads(line)
            for n in data['nouns']:
                if n not in frequencies:
                    frequencies[n] = 0
                frequencies[n] += 1

    cloud = wordcloud.WordCloud(font_path='font.ttf').generate_from_frequencies(frequencies)
    img = cloud.to_image()
    img.save('out.png')
