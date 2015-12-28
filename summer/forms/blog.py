from wtforms.fields import StringField, HiddenField, TextAreaField
from wtforms.validators import DataRequired
from wtforms_tornado import Form

class BlogPostForm(Form):
    topic = StringField('General topic')
    keywords = StringField('Keywords')

    title = StringField('Title', validators=[DataRequired()])
    summary = TextAreaField('Summary', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
