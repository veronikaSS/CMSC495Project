from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, RadioField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from flask import flash
from budget_tracker.model import User
import plaid
import settings as settings
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

class TransactionForm(FlaskForm):
    transaction_item = StringField("Transaction Name", validators=[DataRequired()])
    transaction_description = StringField("Transaction Description", validators=[DataRequired()])
    transaction_category = RadioField("Category", choices=[])
    transaction_amount= DecimalField("Amount", validators=[DataRequired()])
    transaction_category= SubmitField("Add Transaction")

class SavingsGoalForm(FlaskForm):
    savings_goal_name = StringField("Savings Goal Name", validators=[DataRequired()])
    savings_goal_amount= DecimalField("Amount", validators=[DataRequired()])
    savings_goal_date_number = IntegerField("Number", validators=[DataRequired()])
    savings_goal_date_unit = StringField("Date", validators=[DataRequired()])
    transaction_category= SubmitField("Save")
