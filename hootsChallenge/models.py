from .extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    mathScore = db.Column(db.Integer, nullable=False, default = 0)
    natureScienceScore = db.Column(db.Integer, nullable=False, default = 0)
    mathLevel = db.Column(db.Integer, nullable=False, default = 1)
    natureScienceLevel = db.Column(db.Integer, nullable=False, default = 1)

