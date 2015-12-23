from tornado.web import RequestHandler

from winter.utils import DotDict

class BaseHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self._meta_obj = None

    @property
    def meta(self):
        """ Return singletons and factory methods related to the underlying
            tornado.web.Application object. """

        if self._meta_obj is not None:
            return self._meta_obj
        if hasattr(self.application, 'meta'):
            self._meta_obj = DotDict(self.application.meta)
        return self._meta_obj


class MainHandler(BaseHandler):
    def get(self):
        self.render('index.html', title='123')