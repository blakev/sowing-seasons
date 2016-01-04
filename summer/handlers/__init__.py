import os

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
            'request': self.request,
            'seo': self.application.meta.seo,
            'settings': self.settings,
            'this_url': '%s://%s%s' % (self.request.protocol, self.request.host, self.request.uri),
            'xsrf_token': self.xsrf_token,
            'xsrf_form_html': self.xsrf_form_html })
        self.write(self.render_template(name, **kwargs))

    @property
    def meta(self):
        if self._meta is None and hasattr(self.application, 'meta'):
            self._meta = DotDict(self.application.meta)
        return self._meta
