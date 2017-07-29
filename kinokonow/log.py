import os
import logging.config


logger = logging.getLogger(__name__)


script_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.join(script_dir, os.path.pardir)
logs_dir = os.path.join(parent_dir, 'logs')


def setup_worker():
    """
    稼働中に設定を更新する事は多分無く、
    yamlとして定義するメリットはあまり感じられないので辞書として定義する
    無駄な依存性は増やさないためにロギング設定は任意なので失敗したらそのまま進む
    """
    config = {
        'disable_existing_loggers': False,
        'formatters': {'fmt': {'datefmt': '%Y-%m-%d %H:%M:%S',
                               'format': '%(asctime)s %(module)s %(funcName)s '
                                         '%(message)s'}},
        'handlers': {'console': {'class': 'logging.StreamHandler',
                                 'formatter': 'fmt',
                                 'level': 'INFO',
                                 'stream': 'ext://sys.stdout'},
                     'file': {'backupCount': 3,
                              'class': 'logging.handlers.RotatingFileHandler',
                              'filename': os.path.join(logs_dir, 'log.txt'),
                              'formatter': 'fmt',
                              'level': 'DEBUG',
                              'maxBytes': 10000000}},
        'loggers': {'oauthlib.oauth1.rfc5849': {'level': 'WARNING'},
                    'requests': {'level': 'WARNING'},
                    'requests_oauthlib': {'level': 'WARNING'}},
        'root': {'handlers': ['console', 'file'], 'level': 'DEBUG'},
        'version': 1}
    if os.path.exists(logs_dir):
        try:
            logging.config.dictConfig(config)
            logger.info('Configured logging')
            logger.debug('Configured logging')
        except ValueError:
            pass
