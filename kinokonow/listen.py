import re
import os
import csv
from twython import TwythonStreamer
from kinokonow import settings, tasks, database


class Streamer(TwythonStreamer):
    def on_error(self, status_code, data):
        print(status_code)
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


if __name__ == '__main__':
    users_to_follow = get_users_to_follow()
    print('Following %d users' % len(users_to_follow))
    white_list = AllowedSources.init()

    def on_success(data):
        if 'text' in data:
            source = extract_source(data['source'])
            if not white_list.is_allowed(source):
                print('source %s is not allowed' % source)
                return
            user_id = data['user']['id']
            if user_id not in users_to_follow:
                print('Not following user id %d' % user_id)
                pass
            print(data['user']['screen_name'], ':', data['text'], '\n')
            database.save_tweet(data)
            tasks.create_noun_extraction_task(data['text']).delay()

    stream = get_streamer()
    stream.on_success = on_success
    stream.statuses.filter(follow=','.join(users_to_follow))
