from datetime import datetime
from flask_login import UserMixin
import secrets
from budget_tracker import db, login_manager
import random


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(48), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password

class PlaidItem(db.Model):
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    access_token = db.Column(db.String(200), unique=True)
    item_id = db.Column(db.String(200), unique=True)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plaid_account_id = db.Column(db.Text(200), primary_key=True, nullable=True, unique=True)
    balances = db.Column(db.Float, nullable=True)
    mask = db.Column(db.Text(200), nullable=True)
    name = db.Column(db.Text(200), nullable=True)
    official_name = db.Column(db.String(200), nullable=True)
    subtype = db.Column(db.String(200), nullable=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, default=None)
    item  = db.Column(db.Integer, db.ForeignKey('plaid_item.item_id'), nullable=False,default=None)

# class Budget(db.Model):
#     date = db.Column(db.DateTime, nullable=False)
#     user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, default=None)

    def __str__(self):
        return self.budget_text

class Category(db.Model):
    description = db.Column(db.Text(200), unique=True, nullable=False)
    parent_category =  db.Column(db.String(200),  primary_key=True, nullable=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, default=None)
    custom = db.Column(db.Boolean, default=False, nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, auto=True)
    account = db.Column(db.ForeignKey('account'), null=True, blank=True)
    account_owner = db.Column(db.String(200), null=True)
    amount = db.Column(db.Float(12), decimal_places=2, null=True)
    authorized_date = db.Column(db.DateTime, null=True)
    builtin_category =db.Column(db.ForeignKey('Category'), null=True, blank=True)
    category_id = db.Column(db.String(200), null=True)
    date =db.Column(db.DateTime, null=False, default=datetime.now())
    iso_currency_code = db.Column(db.String(200), null=True)
    location =db.Column(db.String(200), null=True)
    merchant_name = db.Column(db.String(200), null=True)
    name = db.Column(db.String(200), null=True)
    payment_meta = db.Column(db.String(200), null=True)
    payment_channel = db.Column(db.String(200), null=True)
    pending = db.Column(db.Boolean, null=True)
    pending_transaction_id = db.Column(db.String(200), null=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __str__(self):
        return self.transaction_text
