from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=5, max=100)])
    submit = SubmitField("Login")


class ConsoleCommand(FlaskForm):
    console_command = StringField('Command',
                                  validators=[DataRequired()])
    submit_weapon = SubmitField("Weapon")