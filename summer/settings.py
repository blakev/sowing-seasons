import uuid

DEBUG = True
CSRF_SECRET = 'woopsss' #uuid.uuid4().hex

APP_CONFIG = {
    'port': 8888
}

SEO_VALUES = {
    'title': 'SowingSeasons - takes awhile to grow anything.',
    'keywords': 'technology,programming,python',
    'description': '',
    'author': 'Blake VandeMerwe <blakev@null.net>',
    'author_name': 'Blake VandeMerwe',
    'author_email': 'blakev@null.net',

    'google': {
        'author_id': '+BlakeVandeMerwe'
    },

    'img': r'/static/img/profile.jpg'
}

TORNADO_CONFIG = {
    'compress_response': True,
    'login_url': '/login',

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