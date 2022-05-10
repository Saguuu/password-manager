from . import db 
from flask_login import UserMixin

class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    website = db.Column(db.String(150))
    password = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    name = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    secret_question = db.Column(db.String(150))
    secret_question_answer = db.Column(db.String(150))
    tier = db.Column(db.Integer, default=0)
    passwords = db.relationship("Password")
