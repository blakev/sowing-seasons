from tornado.web import Application

from winter.search import obtain_index, WinterSchema
from winter.settings.default import TORNADO_APP_CONFIG, WHOOSH
from winter.utils import DotDict
from winter.views import MainHandler

# easier access when configs are dot dictionaries
WHOOSH = DotDict(WHOOSH)


def make_app(**settings):

    # initialize the main application
    app = Application([

        (r'/', MainHandler)

    ], **settings)

    app.settings.update(TORNADO_APP_CONFIG)

    # application-wide meta object
    # to obtain singletons/factory methods
    app.meta = DotDict()

    # set the whoosh search index
    app.meta.search_index = obtain_index(
            WHOOSH.location, WinterSchema, WHOOSH.index_name)

    return app
