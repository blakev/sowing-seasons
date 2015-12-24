import os

from tornado.web import Application, StaticFileHandler, url

from winter.search import obtain_index, WinterSchema
from winter.search.handlers import SearchHandler
from winter.settings.default import TORNADO_APP_CONFIG, WHOOSH
from winter.utils import DotDict
from winter.views import MainHandler

# easier access when configs are dot dictionaries
WHOOSH = DotDict(WHOOSH)


def make_app(**settings):

    static_path = os.path.join(os.getcwd(), 'static')

    # initialize the main application
    app = Application([

        url(r'/', MainHandler, name='index'),
        url(r'/search/', SearchHandler, name='search'),
        url(r'/static/(.*)', StaticFileHandler, {'path': static_path})

    ], **settings)

    app.settings.update(TORNADO_APP_CONFIG)

    # application-wide meta object
    # to obtain singletons/factory methods
    app.meta = DotDict()

    # set the whoosh search index
    app.meta.search_index = obtain_index(
            WHOOSH.location, WinterSchema, WHOOSH.index_name)

    return app
