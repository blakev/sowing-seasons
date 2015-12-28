from wtforms.fields import StringField, PasswordField
from wtforms.validators import DataRequired
from wtforms_tornado import Form

class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    auth_token = PasswordField('Auth Token', validators=[DataRequired()])