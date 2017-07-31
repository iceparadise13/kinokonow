import re


def remove_pattern(pat, text):
    return re.sub('%s(?:\s|$)' % pat, '', text)


def remove_mention(text):
    return remove_pattern('@.+?', text)


def remove_url(text):
    return remove_pattern('(?:http|https)://.+?', text)


def remove_rt_boilerplate(text):
    return remove_pattern('RT @.+:', text)


def extract_hash_tags(tweet):
    hashtags = []
    while 1:
        regex = re.search('#(\S+(?#should be greedy))', tweet)
        if not regex:
            break
        tag = regex.group(1)
        hashtags.append(tag)
        tweet = tweet.replace('#' + tag, '')
    return tweet, hashtags


def pre_ma(tweet):
    """
    形態素解析をする前にツイートをプリプロセスする
    :param tweet: 生のツイート
    :return: プリプロセスされたツイートとハッシュタグリストのタプル
    """
    # 文章的に意味を持たないツイッター固有の情報を消す
    tweet = remove_rt_boilerplate(tweet)
    tweet = remove_mention(tweet)
    tweet = remove_url(tweet)
    # 「#」はJumanppに渡すとハングする上に、
    # 外国で見るようなハッシュタグを文章中の単語として使う文化は日本に無いのでそのまま抽出する
    tweet, hash_tags = extract_hash_tags(tweet)
    # 半角スペースが入っているとJumanppの挙動がおかしくなるので消す
    # 他のフィルターに支障が出るので最後に実行する
    return tweet, hash_tags
