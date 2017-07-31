from kinokonow import filter


def lower(tweet):
    return tweet.lower()


def normalize_tweet(tweet):
    """
    検索用にツイートを正規化する
    :param tweet: 生のツイート
    :return: 正規化したツイート
    """
    # 他のフィルターを先に実行すると支障をきたすので始めにRTのボイラープレートを除去する
    tweet = filter.remove_rt_boilerplate(tweet)
    tweet = filter.remove_mention(tweet)
    tweet = filter.remove_url(tweet)
    tweet = lower(tweet)
    return tweet


def normalize_search_query(query):
    return lower(query)
