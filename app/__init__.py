import secrets
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)


app.config["SECRET_KEY"] = secrets.token_hex(32)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///nyr.db'
db = SQLAlchemy(app)
app.app_context().push()

bcrypt = Bcrypt(app)

from app import admin_routes
from app import main_routes
from app import models

db.create_all()

