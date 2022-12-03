from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from flask import flash
from budget_tracker.model import User
import plaid
import settings
from plaid.api import plaid_api


# Available environments are
# 'Production'
# 'Development'
# 'Sandbox'
def plaid_obj(self):
    configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox,
        api_key={
            'clientId': settings.PLAID_CLIENT_ID,
            'secret': settings.PLAID_SECRET_KEY_DEV,
        }
    )

    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)

    return client


class RegisterForm(FlaskForm):
    email = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password",
                             validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField("Confirm Password")
    submit = SubmitField("Register")

    # validation from checking the email
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError(
                "Username Already Taken. Please Choose Another One")


class LoginForm(FlaskForm):
    email = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class UpdatePasswordForm(FlaskForm):
    password = PasswordField("Enter New Password", validators=[
                             DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField("Confirm New Password")
    submit = SubmitField("Update Password")
