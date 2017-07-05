import re
import json
import MeCab
import wordcloud


def extract_nouns(text):
    mecab = MeCab.Tagger('-Ochasen')
    parsed = mecab.parse(text)
    nouns = []
    for chunk in parsed.splitlines()[:-1]:
        split = chunk.split('\t')
        if split[3].startswith('名詞'):
            nouns.append((split[0], split[3]))
    return nouns


def remove_pattern(pat, text):
    return re.sub('%s(?:\s|$)' % pat, '', text)


def remove_mention(text):
    return remove_pattern('@.+?', text)


def remove_url(text):
    return remove_pattern('(?:http|https)://.+?', text)


def remove_rt_boilerplate(text):
    return remove_pattern('RT @.+:', text)


def clean(text):
    text = remove_rt_boilerplate(text)
    text = remove_url(text)
    return remove_mention(text)


if __name__ == '__main__':
    frequencies = {}
    with open('out.txt') as f:
        while 1:
            line = f.readline()
            if not line:
                break
            data = json.loads(line)
            text = data['text']
            print(data['user']['screen_name'], ':', data['text'])
            text = clean(text)
            print('cleaned: ' + text)
            nouns = extract_nouns(text)
            print('nouns: %s' % ' '.join(['%s(%s)' % (noun, desc) for noun, desc in nouns]))
            for noun, desc in nouns:
                if noun not in frequencies:
                    frequencies[noun] = 0
                frequencies[noun] += 1
            print()
        cloud = wordcloud.WordCloud(font_path='font.ttf').generate_from_frequencies(frequencies)
        img = cloud.to_image()
        img.save('out.png')
