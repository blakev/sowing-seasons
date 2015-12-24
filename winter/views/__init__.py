
import simplejson as json
from tornado import gen
from tornado.web import RequestHandler, authenticated
from whoosh.query import Every

from winter.search import get_default_schema, write_index, update_index
from winter.search.queries import generic, get_all_documents, get_one_document
from winter.utils import DotDict

class BaseHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self._meta_obj = None

    def get_current_user(self):
        user_id = self.get_secure_cookie('user_id', None)
        return user_id

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
    @gen.coroutine
    def get(self):
        posts = yield generic(self.meta.search_index, q=Every(), limit=10)
        self.render('index.html', posts=posts)


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html', error=None)

    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        auth_key = self.get_argument('auth_key')

        if auth_key == self.meta.auth_token and \
            self.meta.users.get(username, None) == password:
            self.set_secure_cookie('user_id', username)
            self.redirect('/create')
        else:
            self.render('login.html', error="cannot authenticate you")


class CreateDocumentHandler(BaseHandler):
    @authenticated
    @gen.coroutine
    def get(self):
        # get all the posts we have in the search index
        by_id = self.get_argument('post_id', None)

        if not by_id:
            results = yield get_all_documents(self.meta.search_index)
        else:
            results = yield get_one_document(self.meta.search_index, by_id)

        # are we making a new document?
        create_new = not by_id

        self.render('create.html', results=results, new_doc=create_new)

    @authenticated
    @gen.coroutine
    def post(self):
        by_id = self.get_argument('post_id', None)

        fields = get_default_schema()
        fields.update({
            'title': self.get_argument('title'),
            'keywords': self.get_argument('keywords'),
            'summary': self.get_argument('summary'),
            'content': self.get_argument('content')
        })

        if by_id:
            fields['uuid'] = by_id
            deleted = yield update_index(self.meta.search_index, **fields)

            if not deleted:
                self.redirect('/create?post_id=%d' % int(fields['uuid']))

        else:
            yield write_index(self.meta.search_index, **fields)

        self.redirect('/create')
