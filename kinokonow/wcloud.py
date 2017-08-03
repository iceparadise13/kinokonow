import wordcloud


def generate(frequencies, **kwargs):
    return wordcloud.WordCloud(**kwargs).generate_from_frequencies(frequencies).to_image()
