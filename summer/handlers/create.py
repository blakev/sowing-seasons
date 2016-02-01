import os
import uuid

from tornado import gen
from tornado.web import authenticated

from summer.forms.blog import BlogPostForm
from summer.handlers import BaseHandler
from summer.ext.search import get_default_schema, write_index, update_index
from summer.ext.search.queries import get_all_documents, get_one_document
from summer.utils.img import process_banner_file

FIELDS = ['title', 'topic', 'keywords', 'summary', 'content', 'pmeta']
LOWER_FIELDS = ['topic', 'keywords']

class AdminCreateHandler(BaseHandler):
    @authenticated
    @gen.coroutine
    def post(self):
        by_id = self.get_argument('post_id', None)
        idx = self.meta.search_index

        if by_id:
            # updating document
            post, _ = yield get_one_document(self.meta.search_index, by_id=by_id)
            fields = post.results[0]
        else:
            # document doesn't exist, potentially
            fields = get_default_schema(idx.schema)

        # clean missing fields
        if fields['pmeta'] is None: fields['pmeta'] = '{}'
        if fields['created'] is None: fields['created'] = fields['modified']

        fields.update({f:self.get_argument(f) for f in FIELDS})
        for f in LOWER_FIELDS:
            fields[f] = fields[f].lower()

        clear_statics = self.get_arguments('clear_statics') == 'y'
        clear_banner = self.get_arguments('clear_banner') == 'y'

        if clear_statics:
            fields['statics'] = None

        if clear_banner:
            fields['banner'] = None

        banner_file = self.request.files.get('banner', None)

        # there was a file upload with this post
        if banner_file:
            for f in banner_file:
                fields['banner'] = process_banner_file(f, self.meta.settings.media, by_id)

        redirect_url = '/admin/create'
        is_delete = fields['title'] in ('', None,)

        if by_id:
            fields['uuid'] = by_id
            # should we delete this post?
            yield update_index(idx, is_delete, **fields)

        else:
            # we need the ID from uuid, because this is a new
            # post, as opposed to setting the UUID from the id
            # generated from the "all results" search request.
            by_id = fields['uuid']
            yield write_index(idx, **fields)

        if not is_delete:
            redirect_url += '?post_id=%s' % by_id

        return self.redirect(redirect_url)


    @authenticated
    @gen.coroutine
    def get(self):
        # are we looking at a single document, or a list of documents?
        by_id = self.get_argument('post_id', None)

        all_posts = yield get_all_documents(self.meta.search_index)
        form = BlogPostForm()

        if by_id:
            post, _ = yield get_one_document(self.meta.search_index, by_id=by_id)
            post = post.results[0]
            if post:

                for f in FIELDS:
                    getattr(form, f, f).data = post[f]

        else:
            post = None

        new_doc = by_id is None

        self.render_html('pages/create.html', all_posts=all_posts, new_doc=new_doc, form=form, post=post)