import math


class TfIdf(list):
    @staticmethod
    def _count_words(document):
        return sum(document.values())

    def _tf(self, word, document):
        """
        `document`における`word`のtf値を (`document`における`word`の出現数) / (`document`の合計単語数) で計算する
        :param word:
        tf値を計算する単語
        :return:
        tf値
        """
        return document.get(word, 0) / self._count_words(document)

    def _get_occurred_documents(self, word):
        return len([s for s in self if word in s])

    def _idf(self, word):
        """
        `word`のidf値をlog10((ドキュメントの数)/全ドキュメントにおける`word`の出現数)で計算する
        式をそのまま使うと全ドキュメントにおける頻出語のペナルティーが少ないので自乗して補う
        :param word:
        idf値を計算する単語
        :return:
        idf値
        """
        # `word`が過去のドキュメントで一度も参照されていない場合、
        # ゼロ除算が起こってしまうのでidfの計算を飛ばして1を返して`tf`の値のみをスコアに反映させる
        od = self._get_occurred_documents(word)
        return math.log10(len(self) / od) ** 2 if od else 1

    def __call__(self, word, document):
        return self._tf(word, document) * self._idf(word)


def score(document, past_documents):
    """
    `document`中の全ての単語のtfidf値を計算してスコアの辞書を返す
    :param document:
    tfの計算に使う現在のドキュメント
    :param past_documents:
    idfの計算に使う過去のドキュメント
    :return:
    tfidf値の辞書
    """
    tfidf = TfIdf(past_documents)
    return dict([(word, tfidf(word, document)) for word in document])
