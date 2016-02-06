from wtforms.fields import StringField
from wtforms.validators import DataRequired, Length
from wtforms_tornado import Form

class SearchForm(Form):
    query = StringField('Query', validators=[DataRequired(), Length(min=4, max=100)])