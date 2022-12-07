from flask import Flask,request,jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy,sqlalchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from budget_tracker.utils import *
from flask import Flask

app = Flask(__name__)

app.config["SECRET_KEY"] = 'CMSC495'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

try:
    db = SQLAlchemy(app)
except sqlalchemy.exc.ProgrammingError as e:
    print("error",e)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


from budget_tracker import routes
routes.db.create_all()