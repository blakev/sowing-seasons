import uuid

def contents_of(f):
    with open(f, 'r') as ins_file:
        contents = ' '.join(ins_file.readlines())
    return contents

DEBUG = True
CSRF_SECRET = 'blake' # uuid.uuid4().hex

APP_CONFIG = {
    'port': 8888,
    'host': '127.0.0.1',
    'domain': 'sowingseasons.com',
    'protocol': 'https', # we don't support HTTP on the WildWildWeb
    'media': r'/home/blake/temp/sowing-seasons-media'
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