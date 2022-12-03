from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from budget_tracker import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from budget_tracker.form import LoginForm, RegisterForm, UpdatePasswordForm
from flask_sqlalchemy import sqlalchemy
from budget_tracker.model import User
from budget_tracker.functions import is_valid_password, is_common_password
from datetime import datetime
import logging
from flask import session


""" failed logins log to log failed login attempts"""
log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)
fileHandler = logging.FileHandler('failed_login_attempts.log')
format = logging.Formatter(r'%(asctime)s: %(message)s')
fileHandler.setFormatter(format)
log.addHandler(fileHandler)


@app.route('/')
@login_required
def index():
    # home page
    now = datetime.now().strftime("%A, %d-%m-%Y %H:%M")
    return render_template('index.html', now=now)


@app.route('/transactions', methods=['GET'])
@login_required
def transactions():
    # transactions page
    now = datetime.now().strftime("%A, %d-%m-%Y %H:%M")
    return render_template("transactions.html", now=now)


@app.route('/spending', methods=['GET'])
@login_required
def spending():
    now = datetime.now().strftime("%A, %d-%m-%Y %H:%M")
    return render_template("spending.html", now=now)


@app.route('/saving', methods=['GET'])
@login_required
def saving():
    # savings page
    now = datetime.now().strftime("%A, %d-%m-%Y %H:%M")
    return render_template("saving.html", now=now)


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    # loading the form
    login = LoginForm()
    if login.validate_on_submit():
        user = User.query.filter_by(email=login.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login.password.data):
            next_page = request.args.get("next")
            login_user(user)
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            ip_address = request.remote_addr
            log.warning("%s", ip_address)
            flash("Login unsuccessful Please Check Username and Password", "danger")
    return render_template("login.html", form=login)


@app.route("/register", methods=["GET", "POST"])
def register():
    # checking if the current user is logged
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    register = RegisterForm()
    if register.validate_on_submit():
        password = register.password.data
        if is_common_password(password):
            if is_valid_password(password):
                hashed_password = bcrypt.generate_password_hash(
                    password).decode("utf-8")
                try:
                    user = User(email=register.email.data,
                                password=hashed_password)
                    db.session.add(user)
                    db.session.commit()
                except sqlalchemy.exc.IntegrityError:
                    flash("User By That Username Exists", "warning")
                flash(f"Account Created successfully", "success")
                return redirect(url_for('login'))
            else:
                flash(
                    f"Password does not meet requirements. Needs to be 12 characters(1 uppercase character, 1 lowercase character, 1 number and 1 special character)",
                    "warning")
        else:
            flash(f"Error! The password provided is common and has been compromised before. Please Change", "danger")
    return render_template("register.html", form=register)


@app.route("/update/password", methods=["GET", "POST"])
def update_password():
    update = UpdatePasswordForm()
    if update.validate_on_submit():
        password = update.password.data
        if is_common_password(password):
            if is_valid_password(password):
                hashed_password = bcrypt.generate_password_hash(
                    password).decode("utf-8")
                user_logged_in = current_user
                user_logged_in.password = hashed_password
                db.session.commit()
                flash(f"Password Updated successfully", "success")
            else:
                flash(
                    f"Password does not meet requirements. Needs to be 12 characters (1 uppercase character, 1 lowercase character, 1 number and 1 special character)",
                    "warning")
        else:
            flash(f"Error! The password provided is common and has been compromised before. Please Change", "danger")
    now = datetime.now().strftime("%A, %d-%m-%Y %H:%M")
    return render_template("update_password.html", form=update, now=now)
