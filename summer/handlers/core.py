from collections import Counter

from pyatom import AtomFeed
from tornado import gen
from whoosh.query import Every

from summer.ext.search import document_slug
from summer.ext.search.queries import get_all_documents, generic
from summer.forms.user import LoginForm
from summer.handlers import BaseHandler, fn_markdown
from summer.utils import DotDict

class IndexHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        posts = yield generic(self.meta.search_index, q=Every())
        topics = self.get_topics(posts)
        keywords = self.get_keywords(posts)
        return self.render_html('pages/index.html', posts=posts, topics=topics, keywords=keywords)


class AtomFeedHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        posts = yield generic(self.meta.search_index, q=Every(), limit=20)
        feed = AtomFeed(title="SowingSeasons",
                        title_type="text",
                        subtitle="takes awhile to grow anything.",
                        subtitle_type="text",
                        feed_url="https://sowingseasons.com/feed.atom",
                        url="https://sowingseasons.com",
                        author="Blake VandeMerwe",
                        icon="sowingseasons.com/static/img/ico_black.png",
                        logo="sowingseasons.com/static/img/logo.png",
                        rights="MIT LICENSE",
                        rights_type="text",
                        generator=("PyAtom", "https://github.com/sramana/pyatom", "1.4"))
        for post in posts.results:
            post = DotDict(post)
            feed.add(title=post.title,
                     title_type="text",
                     content=fn_markdown(post.content),
                     content_type="html",
                     summary=post.summary,
                     summary_type="text",
                     url='https://sowingseasons.com' + document_slug(post),
                     updated=post.modified,
                     author="Blake VandeMerwe",
                     published=post.modified,
                     rights="MIT LICENSE",
                     rights_type="text")
        self.write(feed.to_string())


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
