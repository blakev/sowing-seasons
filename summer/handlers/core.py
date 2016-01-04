from collections import Counter

from tornado import gen
from whoosh.query import Every

from summer.ext.search.queries import get_all_documents, generic
from summer.forms.user import LoginForm
from summer.handlers import BaseHandler

class IndexHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        keywords = Counter()

        posts = yield generic(self.meta.search_index, q=Every())
        topics = sorted(list(set(post.get('topic', None) for post in posts.results)))

        # extract the most common keywords for the side bar
        for post in posts.results:
            keywords.update([x.strip() for x in post.get('keywords', '').split(',')])
        keywords = keywords.most_common(20)

        return self.render_html('pages/index.html',
                    posts=posts, topics=topics, keywords=keywords)


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
