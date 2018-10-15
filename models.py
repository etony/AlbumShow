from album import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(20), unique=True, index=True)
    email = db.Column(db.String(254), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(30))
    website = db.Column(db.String(255))
    bio = db.Column(db.String(120))
    location = db.Column(db.String(50))
    confirmed = db.Column(db.Boolean, default=False)
    locked = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    member_since = db.Column(db.DateTime, default=datetime.now)
    picture = db.Column(db.String(100), default='images/timg.jpg')
    picture_s = db.Column(db.String(100), default='images/user.jpg')

    def set_password(self,password):
        self.password_hash = generate_password_hash(password,method='pbkdf2:sha256',salt_length=8)

class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500))
    filename = db.Column(db.String(64))
    filename_s = db.Column(db.String(64))
    filename_m = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, default=datetime.now, index=True)
    can_comment = db.Column(db.Boolean, default=True)
    flag = db.Column(db.Integer, default=0)
    author_id = db.Column(db.String(20), db.ForeignKey('users.userid'))
    comments = db.relationship('photoComment', backref='Photo', lazy='dynamic')

class SysLog(db.Model):
    __tablename__ = 'syslog'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(20), db.ForeignKey('users.userid'))
    userName = db.Column(db.String(20))
    operTime = db.Column(
        db.DateTime,
        default=datetime.now,
    )
    operContent = db.Column(db.String(300))

class photoComment(db.Model):
    __tablename__ = 'photocomment'
    id = db.Column(db.Integer, primary_key=True)
    photoid = db.Column(db.Integer, db.ForeignKey('photos.id'))
    comment = db.Column(db.String(500))

# set FLASK_APP=manager.py
# flask shell
# from album import db
# db.create_all()
