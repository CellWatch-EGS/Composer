# models.py

# from flask_login import UserMixin
# from .extensions import db

# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
#     email = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))
#     name = db.Column(db.String(1000))
#     token = db.Column(db.String(1000)) #verificar comprimento necessario

from flask_sqlalchemy import SQLAlchemy
from .extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120))

    def __repr__(self):
        return '<User %r>' % self.username
    
    @property
    def is_active(self):
        # Implement your logic here. This is just an example.
        return True
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_authenticated(self):
        # All users are always considered authenticated.
        return True