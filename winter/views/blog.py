from markdown import markdown
from tornado import gen
from tornado.escape import xhtml_unescape

from winter.search.queries import generic
from winter.views import BaseHandler

class BlogHandler(BaseHandler):
    @gen.coroutine
    def get(self, doc_uuid, slug):
        results = yield generic(self.meta.search_index, qs="uuid:"+str(doc_uuid), limit=1)
        exists = results.get('count', -1) > 0
        post = results.get('results', [])[0] if results and exists else None
        if post:
            post['content'] = markdown(post.get('content', ''))
        self.render('blog_post.html',
            posts=results, post=post, slug=slug, exists=exists)