import os
import json

from tornado.web import Application, StaticFileHandler, url

from summer.ext.search import SowingSchema, obtain_index, get_default_schema
from summer.handlers.blog import BlogHandler
from summer.handlers.core import IndexHandler, LoginHandler
from summer.handlers.create import AdminCreateHandler
from summer.handlers.search import StaticSearchHandler
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
        # hard routes
        url(r'/favicon.ico', StaticFileHandler, {'path': os.path.join(static_path, 'favicon.ico')}),
        url(r'/robots.txt', StaticFileHandler, {'path': os.path.join(static_path, 'robots.txt')}),
        # soft routes
        url(r'/login', LoginHandler),
        url(r'/admin/create', AdminCreateHandler),
        url(r'/search/([a-z]+)/(.*)', StaticSearchHandler),
        url(r'/blog/([a-z]+)/(\d+)/(\d+)/(.*)/(\d+)', BlogHandler),
        # catch-all routes
        url(r'/static/(.*)', StaticFileHandler, {'path': static_path}),
        url(r'/', IndexHandler),
    ], **TORNADO_CONFIG)

    # storage location for singletons and factory methods
    app.meta = DotDict()
    app.meta.seo = SEO_VALUES

    # ~~ config Search
    app.meta.search_index = obtain_index(
        WHOOSH.get('location'), SowingSchema, WHOOSH.get('index_name'))

    # ~~ private settings
    private_settings = json.load(open('private_settings.json', 'r'))
    # bootstrap the private settings into the meta-object accessible
    # in the BaseHandler webRequest class
    app.meta.private = private_settings

    # ~~ authentication
    auth = private_settings.get('auth', {})
    username, password = auth.get('username', None), auth.get('password', None)

    app.meta.auth_token = auth.get('token', None)
    app.meta.username_combo = (username, password,)

    # callback settings for launching the server
    app_settings = DotDict()
    app_settings.update(APP_CONFIG)

    return app, app_settings