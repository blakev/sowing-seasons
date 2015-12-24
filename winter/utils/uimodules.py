from markdown import markdown
from tornado.web import UIModule

class BlogPost(UIModule):
    def render(self, post):
        post['content'] = markdown(post['content'])
        return self.render_string('_blog_post.html', post=post)