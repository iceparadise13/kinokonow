import mock
import unittest
import yahooma


class TestCase(unittest.TestCase):
    def setUp(self):
        fixture = b'<?xml version="1.0" encoding="UTF-8" ?>' \
                  b'<ResultSet xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:yahoo:jp:jlp" ' \
                  b'          xsi:schemaLocation="urn:yahoo:jp:jlp ' \
                  b'          https://jlp.yahooapis.jp/MAService/V1/parseResponse.xsd">' \
                  b'<ma_result>' \
                  b'<total_count>2</total_count>' \
                  b'<filtered_count>2</filtered_count>' \
                  b'<word_list>' \
                  b'    <word>' \
                  b'        <surface>\xe6\x97\xa5\xe6\x9c\xac\xe4\xba\xba</surface>' \
                  b'        <reading>\xe3\x81\xab\xe3\x81\xbb\xe3\x82\x93\xe3\x81\x98\xe3\x82\x93</reading>' \
                  b'        <pos>\xe5\x90\x8d\xe8\xa9\x9e</pos>' \
                  b'    </word>' \
                  b'    <word>' \
                  b'        <surface>\xe3\x81\xa7\xe3\x81\x99</surface>' \
                  b'        <reading>\xe3\x81\xa7\xe3\x81\x99</reading>' \
                  b'        <pos>\xe5\x8a\xa9\xe5\x8b\x95\xe8\xa9\x9e</pos>' \
                  b'    </word>' \
                  b'</word_list>' \
                  b'</ma_result>' \
                  b'</ResultSet>'
        self.session = mock.MagicMock()
        self.session.get.return_value = mock.MagicMock(content=fixture)
        self.yahoo_api = yahooma.YahooApi('api_key', self.session)
        self.result = self.yahoo_api.parse('日本人です')

    def test_parse(self):
        expected = [('日本人', '名詞'), ('です', '助動詞')]
        self.assertEqual(expected, self.result)

    def test_url(self):
        self.session.get.assert_called_once_with(
            'https://jlp.yahooapis.jp/MAService/V1/parse?appid=api_key&sentence=日本人です')


if __name__ == '__main__':
    unittest.main()
