from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):

    identifier = StringField(
        'Identifier',
        validators=[DataRequired()]
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )

    remember = BooleanField('Remember Me')


class SignupForm(FlaskForm):

    username = StringField(
        'Username',
        validators=[DataRequired()]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8)
        ]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password')
        ]
    )