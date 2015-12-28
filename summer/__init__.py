import os

from tornado.web import Application, StaticFileHandler, url

from summer.ext.search import SowingSchema, obtain_index, get_default_schema
from summer.handlers.core import IndexHandler, LoginHandler
from summer.handlers.create import AdminCreateHandler
from summer.settings import TORNADO_CONFIG, WHOOSH, APP_CONFIG, SEO_VALUES
from summer.utils import DotDict

def make_app(**settings):

    cwd = os.getcwd()

    TORNADO_CONFIG.update(settings)

    # determine where our flat assets are stored
    static_path = os.path.join(cwd, 'static')
    template_path = os.path.join(cwd, 'templates')

    TORNADO_CONFIG['static_path'] = settings.get('static_path', static_path)
    TORNADO_CONFIG['template_path'] = settings.get('template_path', template_path)

    # set up our routing configuration
    app = Application([

        (r'/', IndexHandler),
        (r'/login', LoginHandler),
        (r'/admin/create', AdminCreateHandler),

        url(r'/static/(.*)', StaticFileHandler, {'path': static_path})

    ], **TORNADO_CONFIG)

    # storage location for singletons and factory methods
    app.meta = DotDict()
    app.meta.seo = SEO_VALUES

    # ~~ config Search
    app.meta.search_index = obtain_index(
        WHOOSH.get('location'), SowingSchema, WHOOSH.get('index_name'))

    # ~~ authentication
    with open('auth_credentials', 'r') as auth_file:
        app.meta.auth_token = auth_file.readline().strip()
        app.meta.username_combo = auth_file.readline().strip().split(',')

    # callback settings for launching the server
    app_settings = DotDict()
    app_settings.update(APP_CONFIG)

    return app, app_settings