import os
import uuid

DEBUG = True

WHOOSH = {
    'index_name': 'sowing-seasons',
    'location': r'/home/blake/temp/sowing-seasons-index'
}

TORNADO_APP_CONFIG = {
    'compress_response': True,

    'cookie_secret': 'secrets~!', # uuid.uuid4().hex,
    'login_url': '/login',
    'xsrf_cookies': True,

    # templates
    'compiled_template_cache': not DEBUG,
    'template_path': 'templates',

    # static files
    'static_hash_cache': not DEBUG,
}