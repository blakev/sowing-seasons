import os
import sys
from collections import Counter

import psutil
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from markdown import markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from tornado import web

from summer.ext.search import document_slug
from summer.utils import DotDict
from summer.utils.fn import code_highlighter

DEFAULT_TEMPLATE_PATH = os.path.join(os.getcwd(), 'templates')

fn_markdown = lambda x: markdown(x, extensions=[FencedCodeExtension()])
fn_split = lambda x, y: str(x).split(y)
fn_strip = lambda x: str(x).strip()

def datetime_format(value, format='%m-%d-%Y'):
    return value.strftime(format)

def get_system_load():
    return {
        'cpu': psutil.cpu_percent(interval=None),
        'memory': psutil.virtual_memory(),
        'sys': 'python ' + sys.version.split('(')[0] + sys.platform
    }

class TemplateRender(object):
    """ Class to hold HTML template rendering methods. """

    def render_template(self, name, **kwargs):
        template_path = self.settings.get('template_path', DEFAULT_TEMPLATE_PATH)
        env = Environment(loader=FileSystemLoader([template_path]))

        # filters
        env.filters['datetime_format'] = datetime_format
        env.filters['highlight'] = code_highlighter
        env.filters['markdown'] = fn_markdown
        env.filters['slugify'] = document_slug
        env.filters['split'] = fn_split
        env.filters['strip'] = fn_strip

        try:
            template = env.get_template(name)
        except TemplateNotFound:
            raise TemplateNotFound(name)
        return template.render(kwargs)


class BaseHandler(web.RequestHandler, TemplateRender):

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self._meta = None


    def get_current_user(self):
        return self.get_secure_cookie('user_id', None)


    def render_html(self, name, **kwargs):
        kwargs.update({
            'csrf': self.xsrf_form_html(),
            'current_user': self.get_current_user(),
            'load': get_system_load(),
            'private': self.meta.private,
            'request': self.request,
            'seo': self.meta.seo,
            'settings': self.settings,
            'this_url': self.this_url,
            'xsrf_token': self.xsrf_token,
            'xsrf_form_html': self.xsrf_form_html })
        self.write(self.render_template(name, **kwargs))


    def get_keywords(self, posts, most_common=20):
        keywords = Counter()
        # extract the most common keywords for the side bar
        for post in posts.results:
            keywords.update([x.strip() for x in post.get('keywords', '').split(',')])
        return keywords.most_common(most_common)


    def get_topics(self, posts):
        return sorted(list(set(post.get('topic', None) for post in posts.results)))


    @property
    def meta(self):
        if self._meta is None and hasattr(self.application, 'meta'):
            self._meta = DotDict(self.application.meta)
        return self._meta

    @property
    def this_url(self):
        return '{}://{}{}'.format(
            self.meta.settings.protocol, self.meta.settings.domain, self.request.uri)