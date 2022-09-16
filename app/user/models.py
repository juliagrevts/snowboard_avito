from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True)
    snowboards = db.relationship('Snowboard', backref='user')
    
    def set_password_hash(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password_hash(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'Username: {self.username}, id: {self.id}'
