DEBUG = True

WHOOSH = {
    'index_name': 'sowing-seasons',
    'location': r'/home/blake/temp/sowing-seasons-index'
}

TORNADO_APP_CONFIG = {
    'compress_response': True,

    # templates
    'compiled_template_cache': not DEBUG,
    'template_path': 'templates',

    # static files
    'static_hash_cache': not DEBUG,
    'static_path': 'static',
    'static_url_prefix': '/static/'
}