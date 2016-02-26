import os
import json
import logging
import logging.config

from tornado.web import Application, StaticFileHandler, url

from summer.ext.search import SowingSchema, obtain_index, get_default_schema
from summer.handlers.blog import BlogHandler, OldBlogHandler
from summer.handlers.core import AtomFeedHandler, IndexHandler, LoginHandler, ErrorHandler
from summer.handlers.create import AdminCreateHandler
from summer.handlers.search import DynamicSearchHandler, StaticSearchHandler
from summer.settings import TORNADO_CONFIG, WHOOSH, APP_CONFIG, SEO_VALUES
from summer.utils import DotDict

logger = logging.getLogger(__name__)

def make_app(**settings):
    cwd = os.getcwd()

    TORNADO_CONFIG.update(settings)
    app_settings = DotDict(APP_CONFIG)

    # setup the logging configuration
    logging.config.dictConfigClass(app_settings.logging).configure()

    logger.info('cwd, ' + cwd)
    logger.info('creating application')

    # determine where our flat assets are stored
    static_path = os.path.join(cwd, 'static')
    template_path = os.path.join(cwd, 'templates')

    TORNADO_CONFIG['static_path'] = settings.get('static_path', static_path)
    TORNADO_CONFIG['template_path'] = settings.get('template_path', template_path)

    # set up our routing configuration
    app = Application([
        # hard routes
        url(r'/feed.atom', AtomFeedHandler),
        # soft routes
        url(r'/login', LoginHandler),
        url(r'/admin/create', AdminCreateHandler),
        url(r'/search', DynamicSearchHandler),
        url(r'/search/([a-z0-9_]+)/([a-zA-Z0-9\+\-_\%]+)(\.atom)?', StaticSearchHandler),
        url(r'/blog/([a-zA-Z0-9\-_]+)\.html', OldBlogHandler),
        url(r'/blog/([a-z]+)/(\d+)/(\d+)/(.*)/(\d+)', BlogHandler),
        # catch-all routes
        url(r'/static/(.*)', StaticFileHandler, {'path': static_path}),
        url(r'/media/(.*)', StaticFileHandler, {'path': app_settings.media}),
        url(r'/(.*\.(txt|ico))', StaticFileHandler, {'path': static_path}),
        url(r'/', IndexHandler),
        url(r'/(.*)', ErrorHandler)
    ], **TORNADO_CONFIG)

    logger.info('finished setting up HTTP routes')

    # storage location for singletons and factory methods
    app.meta = DotDict()
    app.meta.seo = SEO_VALUES

    # ~~ config Search
    app.meta.search_index = obtain_index(
        WHOOSH.get('location'), SowingSchema, WHOOSH.get('index_name'))

    logger.info('finished binding to Whoosh index')

    # ~~ private settings
    private_settings = app_settings.pop('private_settings', {})
    # bootstrap the private settings into the meta-object accessible
    # in the BaseHandler webRequest class
    app.meta.private = private_settings

    # ~~ authentication
    auth = private_settings.get('auth', {})
    username, password = auth.get('username', None), auth.get('password', None)

    app.meta.auth_token = auth.get('token', None)
    app.meta.username_combo = (username, password,)

    logger.info('finished configuring authentication')

    # callback settings for launching the server
    app.meta.settings = app_settings

    return app, app_settings