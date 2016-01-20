import json
import os
import uuid

folder, fname = os.path.split(__file__)

def contents_of(f):
    with open(f, 'r') as ins_file:
        contents = ' '.join(ins_file.readlines())
    return contents

DEBUG = bool(int(os.environ.get('SOWING_DEBUG', 1))) # True
CSRF_SECRET = 'mysecretsRsaf3' if DEBUG else uuid.uuid4().hex
LOCAL_SETTINGS = os.environ.get('SOWING_SETTINGS', None)

if LOCAL_SETTINGS is None:
    LOCAL_SETTINGS = os.path.join(folder, 'local-settings.json')

    if not os.path.exists(LOCAL_SETTINGS):
        raise EnvironmentError('no configuration settings `local-settings.py`, %s' % LOCAL_SETTINGS)


APP_CONFIG = {
    'port': 8888,
    'host': '127.0.0.1',
    'domain': 'sowingseasons.com',
    'protocol': 'http' if DEBUG else 'https', # we don't support HTTP on the WildWildWeb
    'media': r'/home/blake/temp/sowing-seasons-media',
    'private_settings': json.load(open(LOCAL_SETTINGS, 'r')),
    'logging': {
        'version': 1,
        'incremental': False,
        'disable_existing_loggers': False,
        'loggers': {
            'summer': {
                'level': 'DEBUG',
                'handlers': ['console', 'file'],
                'qualname': 'sowing',
                'propagate': 0
            }
        },
        'formatters': {
            "default": {
                "format": "%(asctime)s %(ip)-15s  %(levelname)-5s %(name)-40s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        'filters': {
            'traffic': {
                '()': 'summer.ext.logs.IPFilter'
            }
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'level': 'DEBUG',
                'filename': r'/home/blake/temp/sowing-seasons-logs/server.log',
                'maxBytes': 10000000,
                'backupCount': 20,
                'mode': 'a',
                'filters': ['traffic']
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': 'DEBUG',
                'stream': 'ext://sys.stdout',
                'filters': ['traffic']
            }
        }
    }
}

SEO_VALUES = {
    'title': 'SowingSeasons - takes awhile to grow anything.',
    'keywords': 'technology,programming,python',
    'description': contents_of(r'DESCRIPTION'),
    'author': 'Blake VandeMerwe <blakev@null.net>',
    'author_name': 'Blake VandeMerwe',
    'author_email': 'blakev@null.net',

    'google': {
        'author_id': '+BlakeVandeMerwe'
    },

    'img': r'/static/img/profile.jpg',

    'run_analytics': not DEBUG
}

TORNADO_CONFIG = {
    'debug': DEBUG,
    'compress_response': True,

    'cookie_secret': CSRF_SECRET,
    'login_url': '/login',
    'xsrf_cookies': True,

    # static files
    'static_hash_cache': not DEBUG,
}

WHOOSH = {
    'index_name': 'sowing-seasons',
    'location': r'/home/blake/temp/sowing-seasons-index'
}