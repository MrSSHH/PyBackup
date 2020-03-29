from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
app.config['SECRET_KEY'] = 'af7e8e3e25d417f9a0635906dc0325be'

db = SQLAlchemy(app)

from pybackup import routes
