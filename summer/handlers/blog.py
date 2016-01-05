#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 1/3/2016 at 5:20 PM

from tornado import gen

from whoosh.qparser import QueryParser

from summer.ext.search import clean_results, document_slug
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


class OldBlogHandler(BaseHandler):
    @gen.coroutine
    def get(self, old_slug):
        # There are still cached sites from google hitting
        # the server, that don't match the new routing scheme.
        #
        # To compensate for this, the "OldBlogHandler" will
        # parse the previous slug format, and do a broad generic
        # query with the keywords (and title). Since old content
        # is basically being ported 1-to-1, if we have ANY search
        # results, we want to return that page via permanent redirect.
        pieces = list(map(str.strip, old_slug.split('-')))

        idx = self.meta.search_index

        with idx.searcher() as searcher:
            q = QueryParser('title', idx.schema).parse(' OR '.join(pieces))
            results = searcher.search(q, limit=1)
            results = clean_results(idx, results)

        if results.get('count', 0) > 0:
            # rebuild the url, and redirect PERMANENTLY
            # to the correct endpoing
            reslug = document_slug(results.results[0])
            self.redirect(reslug, permanent=True)

        else:
            # we couldn't find a "missing" old article
            # given the slug in the new data store, we need to
            # return some kind of "Missing" page.
            self.write('That content appears to be missing.')
