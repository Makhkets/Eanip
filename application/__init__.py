from flask import Flask, request
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from pyqiwip2p import QiwiP2P




app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = "Aliev@123321asSs"

db = SQLAlchemy(app)
login_manager = LoginManager(app)

QIWI_PRIV_KEY = "eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6InVtZWs3NC0wMCIsInVzZXJfaWQiOiI3OTM4ODk1NDI1MCIsInNlY3JldCI6IjQ1MTdhODNkZDQ3MWEyMDkxNWMwMDg3NGJiNDk5NDhkOGRjODY5NTQzNWY0ZTc1Y2NhMzA2ZGVkNzcxYWY0ZGQifX0="
p2p = QiwiP2P(auth_key=QIWI_PRIV_KEY)

from application import models
from application import routes

def create_db():
    with app.app_context():
        db.create_all()

create_db()
