from collections import Counter

from tornado import gen
from whoosh.query import Every

from summer.ext.search import document_slug
from summer.ext.search.queries import get_all_documents, get_all_topics_and_kw, generic
from summer.forms.user import LoginForm
from summer.handlers import BaseHandler, fn_markdown
from summer.utils import DotDict

class IndexHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        # pagination results
        try:
            page_number = int(self.get_argument('page', 1))
        except ValueError:
            page_number = 1

        idx = self.meta.search_index

        posts = yield generic(idx, q=Every(), page=page_number)
        topics_keywords = yield get_all_topics_and_kw(idx)

        return self.render_html('pages/index.html', posts=posts, **topics_keywords)


class AtomFeedHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        posts = yield generic(self.meta.search_index, q=Every(), limit=20)
        self.write(self.generate_feed(posts))


class LoginHandler(BaseHandler):
    def get(self):
        form = LoginForm()
        self.render_html('pages/login.html', errors=None, form=form)

    def post(self):
        errors = dict()
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        auth_token = self.get_argument('auth_token', None)

        form = LoginForm(self.request.arguments)

        if form.validate():
            def_username, def_password = self.meta.username_combo

            if not all([username, password, auth_token]):
                errors['missing'] = 'missing required field'

            if auth_token != self.meta.auth_token:
                errors['invalid'] = 'invalid authentication token'

            if username != def_username or password != def_password:
                errors['username'] = 'invalid username/password combo'

            if not errors:
                self.set_secure_cookie('user_id', username)
                return self.redirect('/admin/create')

            else:
                form.errors.update(errors)

        self.render_html('pages/login.html', errors=errors, form=form)
