import os

from tornado.web import Application, StaticFileHandler, url

from winter.search import obtain_index, WinterSchema
from winter.search.handlers import SearchHandler
from winter.settings.default import TORNADO_APP_CONFIG, WHOOSH
from winter.utils import DotDict
from winter.views import MainHandler, LoginHandler, CreateDocumentHandler
from winter.views.blog import BlogHandler

# easier access when configs are dot dictionaries
WHOOSH = DotDict(WHOOSH)


def make_app(**settings):

    static_path = os.path.join(os.getcwd(), 'static')

    # initialize the main application
    app = Application([

        url(r'/', MainHandler, name='index'),
        url(r'/blog/([0-9]+)/(.*)', BlogHandler, name='blog'),
        url(r'/search', SearchHandler, name='search'),
        url(r'/login', LoginHandler, name='login'),
        url(r'/create', CreateDocumentHandler, name='new_document'),
        url(r'/static/(.*)', StaticFileHandler, {'path': static_path})

    ], **settings)

    app.settings.update(TORNADO_APP_CONFIG)

    # application-wide meta object
    # to obtain singletons/factory methods
    app.meta = DotDict()

    # set the whoosh search index
    app.meta.search_index = obtain_index(
            WHOOSH.location, WinterSchema, WHOOSH.index_name)

    # VERY BASIC user authentication that
    # gets paired with a server-wide auth token.
    # this system was only meant for one or two people.
    try:
        from winter.settings import users
    except ImportError:
        users = {'default': 'default'}
    app.meta.users = users

    # boot strap the server-wide auth token
    auth_file = open(os.path.join(os.getcwd(), 'settings', 'auth_key'), 'r')
    app.meta.auth_token = auth_file.read()
    auth_file.close()

    return app
