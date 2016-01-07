import os
import uuid

from tornado import gen
from tornado.web import authenticated

from summer.forms.blog import BlogPostForm
from summer.handlers import BaseHandler
from summer.ext.search import get_default_schema, write_index, update_index
from summer.ext.search.queries import get_all_documents, get_one_document

class AdminCreateHandler(BaseHandler):
    @authenticated
    @gen.coroutine
    def post(self):
        by_id = self.get_argument('post_id', None)

        idx = self.meta.search_index

        fields = get_default_schema(idx.schema)
        fields.update({
            'title': self.get_argument('title'),
            'keywords': self.get_argument('keywords').lower(),
            'summary': self.get_argument('summary'),
            'content': self.get_argument('content'),
            'topic': self.get_argument('topic').lower()
        })

        banner_file = self.request.files.get('banner', None)

        # there was a file upload with this post
        if banner_file:
            for f in banner_file:
                short_name = uuid.uuid4().hex[:8]
                orig_extension = f.get('filename', 'Unknown.jpg').split('.')[-1]
                new_name = 'upload_%s.%s' % (short_name, orig_extension)
                new_folder = os.path.join(self.meta.settings.media, str(by_id))
                if not os.path.exists(new_folder):
                    os.makedirs(new_folder)
                new_location = os.path.join(new_folder, new_name)
                with open(new_location, 'wb') as out_file:
                    out_file.write(f.get('body', None))
                fields['statics'] = os.path.join(str(by_id), new_name)

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
                form.title.data = post['title']
                form.topic.data = post['topic']
                form.keywords.data = post['keywords']
                form.summary.data = post['summary']
                form.content.data = post['content']
        else:
            post = None

        new_doc = by_id is None

        self.render_html('pages/create.html', all_posts=all_posts, new_doc=new_doc, form=form, post=post)