#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 1/3/2016 at 5:20 PM

from tornado import gen

from summer.ext.search.queries import get_one_document, documents_last_month
from summer.handlers import BaseHandler

class BlogHandler(BaseHandler):
    @gen.coroutine
    def get(self, topic, year, month, slug, post_uuid):
        idx = self.meta.search_index

        meta_post, related_posts = yield get_one_document(idx, post_uuid)

        if meta_post is None:
            # could not find the blog post entry
            # by the uuid in the url bar..give a 404
            # for now, work on a redirection strategy later.
            self.send_error(status_code=404)

        else:
            meta, post = meta_post, meta_post.results[0]
            self.render_html('pages/blog_post.html', post=post, meta=meta, related=related_posts)