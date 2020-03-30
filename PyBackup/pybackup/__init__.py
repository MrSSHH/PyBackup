from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
app.config['SECRET_KEY'] = 'af7e8e3e25d417f9a0635906dc0325be'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

from pybackup import routes
