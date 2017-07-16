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
    return tweet, []


def preprocess_tweet(tweet):
    """
    Jumanppにデータを渡す前にツイートをプリプロセスする
    :param tweet: 生のツイート
    :return: プリプロセスされたツイートとハッシュタグリストのタプル
    """
    # 文章的に意味を持たないツイッター固有の情報を消す
    tweet = remove_rt_boilerplate(tweet)
    tweet = remove_mention(tweet)
    tweet = remove_url(tweet)
    tweet, hash_tags = extract_hash_tags(tweet)
    # 半角スペースが入っているとJumanppの挙動がおかしくなるので消す
    # 他のフィルターに支障が出るので最後に実行する
    return tweet.replace(' ', ''), hash_tags
