from .extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
   
class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    subjectName = db.Column(db.String(150), nullable=False)

class User_Subject(db.Model):
    __tablename__ = 'user_subject'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, nullable=False)
    subjectId = db.Column(db.Integer, nullable=True)
    score = db.Column(db.Integer, nullable=False, default = 0)
    level = db.Column(db.Integer, nullable=False, default = 1)