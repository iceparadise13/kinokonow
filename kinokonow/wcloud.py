import wordcloud


def generate_image(frequencies, **kwargs):
    # 値が0の要素があるとゼロ除算が起きるので事前に除く
    frequencies = dict([(k, v) for k, v in frequencies.items() if v])
    return wordcloud.WordCloud(**kwargs).generate_from_frequencies(frequencies).to_image()
