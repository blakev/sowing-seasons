from tornado import gen

from winter.search.queries import generic
from winter.views import BaseHandler

class BlogHandler(BaseHandler):
    @gen.coroutine
    def get(self, doc_uuid, slug):
        results = yield generic(self.meta.search_index, qs="uuid:"+str(doc_uuid), limit=1)
        exists = results.get('count', -1) > 0

        self.render('blog_post.html',
            posts=results, post_id=doc_uuid, slug=slug, exists=exists)