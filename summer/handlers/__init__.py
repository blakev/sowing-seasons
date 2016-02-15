import os
import sys
import uuid
import logging
from collections import Counter

import htmlmin
import psutil
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from markdown import markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from pyatom import AtomFeed
from tornado import web

from summer.ext.search import document_slug
from summer.utils import DotDict
from summer.utils.fn import code_highlighter

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATE_PATH = os.path.join(os.getcwd(), 'templates')

fn_markdown = lambda x: markdown(x, extensions=[FencedCodeExtension()])
fn_split = lambda x, y: str(x).split(y)
fn_strip = lambda x: str(x).strip()

def calculate_pagination(res, max_pages=5):
    """ Returns a list of `int`s representing page numbers
        to display at the bottom of a search results page.
    """
    res = DotDict(res)

    # fewer pages than the allowed, return a list
    # with a slot for each
    if res.page_total < max_pages:
        return range(1, res.page_total + 1)

    # towards the end of the pages, we only want to
    # include the `max_pages`
    if res.page_number >= res.page_total - max_pages:
        return range(res.page_total - max_pages, res.page_total + 1)

    # somewhere in the middle
    if max_pages % 2 == 0: # even max pages
        half_page = (max_pages / 2)
        return range(res.page_number - half_page - 1, res.page_number + half_page)

    else: # odd max pages
        half_page = (max_pages // 2)
        return range(res.page_number - half_page, res.page_number + half_page)

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
        custom_filters = [
            ('calculate_pagination', calculate_pagination),
            ('datetime_format', datetime_format),
            ('highlight', code_highlighter),
            ('markdown', fn_markdown),
            ('slugify', document_slug),
            ('split', fn_split),
            ('strip', fn_strip)
        ]

        for fname, fn in custom_filters:
            env.filters[fname] = fn

        try:
            template = env.get_template(name)
        except TemplateNotFound:
            logger.error('Could not find template, %s' % name)
            raise TemplateNotFound(name)
        else:
            logger.info('render_template(%s)' % name)

        page_html = template.render(kwargs)
        o_len = len(page_html)

        # compress HTML repsonse
        if self.settings.get('compress_response', False):
            page_html = htmlmin.minify(page_html, remove_comments=True, keep_pre=True)
            logger.info('compressed html %0.2f percent of original' % ((len(page_html) / float(o_len))*100))

        return page_html


class BaseHandler(web.RequestHandler, TemplateRender):

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self._reqid = str(uuid.uuid4()).split('-')[0]
        self._meta = None

    def on_finish(self):
        remote_ip = self.request.headers.get('X-Forwardxed-For', '??')
        response_time = self.request._finish_time - self.request._start_time

        logger.info('%s=%s' % (self._reqid, remote_ip))
        logger.info('%s, requested: %s' % (self._reqid, self.this_url))
        logger.info('%s, took: %0.4fs' % (self._reqid, response_time))

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
            'this_url_raw': self.this_url.split('?')[0],
            'xsrf_token': self.xsrf_token,
            'xsrf_form_html': self.xsrf_form_html })
        self.write(self.render_template(name, **kwargs))

    @property
    def meta(self):
        if self._meta is None and hasattr(self.application, 'meta'):
            self._meta = DotDict(self.application.meta)
        return self._meta

    @property
    def this_url(self):
        return '{}://{}{}'.format(
            self.meta.settings.protocol, self.meta.settings.domain, self.request.uri)

    @staticmethod
    def get_keywords(posts, most_common=20):
        keywords = Counter()
        # extract the most common keywords for the side bar
        for post in posts.results:
            keywords.update([x.strip() for x in post.get('keywords', '').split(',')])
        return keywords.most_common(None)

    @staticmethod
    def get_topics(posts):
        return sorted(list(set(post.get('topic', None) for post in posts.results)))

    @staticmethod
    def generate_feed(posts, subtitle='', url="https://sowingseasons.com/feed.atom"):
        logger.info('generate_feed(%s)' % url)

        feed = AtomFeed(
            title="SowingSeasons",
            title_type="text",
            subtitle="takes awhile to grow anything. %s" % subtitle,
            subtitle_type="text",
            feed_url=url,
            url="https://sowingseasons.com",
            author="Blake VandeMerwe",
            icon="/static/img/ico_black.png",
            logo="/static/img/logo.png",
            rights="MIT LICENSE",
            rights_type="text",
            generator=("PyAtom", "https://github.com/sramana/pyatom", "1.4")
        )

        for post in posts.results:
            post = DotDict(post)

            feed.add(
                title=post.title,
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
                rights_type="text"
            )

        return feed.to_string()