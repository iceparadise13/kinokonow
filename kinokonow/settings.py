import os
import yaml


def load_yaml(fname):
    return yaml.load(open(fname))


def load_settings():
    # Assuming the root python script is run in the project directory
    return load_yaml(os.environ['KINOKONOW_SETTINGS_PATH'])


def get_twython_settings():
    # There is no way to tell the order so keys should be explicitly specified
    # rather than returning `node.values()`
    node = load_settings()['twitter']
    return [
        node['consumer_key'],
        node['consumer_secret'],
        node['access_token_key'],
        node['access_token_secret']]


def get_yahoo_api_key():
    return load_settings()['yahoo_api_key']
