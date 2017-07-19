from datetime import datetime, timedelta
import database
import tfidf


def score_key_phrases(save):
    """
    保存されている名詞のtfidf値を計算して返す
    単一ツイートの名詞を一つのドキュメントとして扱うとツイートの長さの性質上、
    tfidfが低頻出語を抽出するだけのアルゴリズムになってしまうので、
    一定の時系列の範囲中にあるツイートの名詞全てを一つのドキュメントとして扱う
    ドキュメントをidf用の過去のドキュメントに含めてしまうと一番最初のドキュメントを取得した時に
    全ての単語のidfスコアが0になってワードクラウドが出力出来ないのでドキュメントの保存は最後に行う
    :param save:
    Trueなら計算後現在のドキュメントを保存する
    :return:
    tfidf値の辞書
    実数のスコアはそのままwordcloudライブラリのクラウド生成メソッドに渡しても問題無い
    """
    now = datetime.utcnow()
    document = database.get_noun_frequencies(now - timedelta(hours=1))
    if not document:
        print('Failed to get noun frequencies')
        return {}
    past_documents = database.get_documents(now - timedelta(days=3))
    scores = tfidf.score(document, past_documents)
    if save:
        database.save_document(document, now)
    return scores