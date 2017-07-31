import re
import os
import csv
import logging
from twython import TwythonStreamer
from kinokonow import settings, tasks, database


logger = logging.getLogger(__name__)


class Streamer(TwythonStreamer):
    def on_error(self, status_code, data):
        logger.warning(status_code)
        self.disconnect()


def get_streamer():
    return Streamer(*settings.get_twython_settings())


def get_users_to_follow():
    with open(os.environ['KINOKONOW_FOLLOWS_PATH']) as f:
        return [user_id for _, user_id, _ in csv.reader(f)]


class AllowedSources(list):
    """
    設定ファイルが存在する場合はファイルで指定されてるクライアントを許可する
    読み取りに失敗した場合は全て許可する
    CIのテストをテスト用アカウントのクライアントに依存させたくないがための実装
    """
    @staticmethod
    def init():
        try:
            fname = os.environ['KINOKONOW_SOURCES_PATH']
            sources = open(fname).read().split('\n')
        except (FileNotFoundError, KeyError):
            print('Allowing all sources')
            sources = []
        return AllowedSources(sources)

    def is_allowed(self, source):
        """Allow source if `init` failed somehow or if `source` is whitelisted"""
        return not self or source in self


def extract_source(source):
    regex = re.search('<a.+?>(.+?)</a', source)
    if not regex:
        return ''
    return regex.group(1)


def is_rt(tweet):
    return tweet.startswith('RT')


if __name__ == '__main__':
    users_to_follow = get_users_to_follow()
    logger.info('Following %d users' % len(users_to_follow))
    white_list = AllowedSources.init()

    def on_success(data):
        if 'text' in data:
            screen_name = data['user']['screen_name']
            logger.info('%s:%s\n' % (screen_name, data['text']))

            source = extract_source(data['source'])
            if not white_list.is_allowed(source):
                logger.warning('Source %s is not allowed' % source)
                return

            # idがいつか数字じゃなくなるかもしれないので文字列として処理する
            user_id = data['user']['id_str']
            if user_id not in users_to_follow:
                logger.warning('Not following user %s %s' % (screen_name, user_id))
                return

            # リツイートは処理の方針が固まるまで無視する
            if is_rt(data['text']):
                logger.warning('Ignoring RT %s' % data['text'])
                return

            database.save_tweet(data)
            tasks.create_noun_extraction_task(data['text']).delay()

    stream = get_streamer()
    stream.on_success = on_success
    stream.statuses.filter(follow=','.join(users_to_follow))
