import json

from wtforms.fields import StringField, HiddenField, TextAreaField, FileField, BooleanField
from wtforms.validators import DataRequired
from wtforms_tornado import Form

class BlogPostForm(Form):
    topic = StringField('General topic')
    keywords = StringField('Keywords')

    title = StringField('Title', validators=[DataRequired()], description='Main title of the post, type <b>DELETE</b> to permanently remove document.')
    author = StringField('Author', validators=[DataRequired()], default='Blake VandeMerwe')
    pmeta = TextAreaField('Meta', validators=[DataRequired()], default='{}')
    summary = TextAreaField('Summary', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

    banner = FileField('Article Banner')

    clear_statics = BooleanField('Clear statics?')
    clear_banner = BooleanField('Clear banner?')


    def validate_pmeta(form, field):
        try:
            if field.data is not None and len(field.data) > 0:
                json.loads(field.data)
        except Exception as e:
            raise e
