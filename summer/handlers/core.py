from tornado import gen

from summer.ext.search.queries import get_all_documents
from summer.forms.user import LoginForm
from summer.handlers import BaseHandler
from summer.handlers.create import AdminCreateHandler

class IndexHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        posts = yield get_all_documents(self.meta.search_index, limit=10)
        return self.render_html('pages/index.html', posts=posts)


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
