from datetime import datetime
import datetime

from flask_login import UserMixin
from flask import current_app
from app import db, login_manager
import jwt
import os

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)
TZ_TAIPEI = datetime.timezone(datetime.timedelta(hours=+8))
datetime.datetime.now(TZ_TAIPEI)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(140), unique=True, nullable=False)
    avatar_path = db.Column(db.String(140), default='/static/asset/default_avatar.png')

    # Foreign Key: User and Post, one to many.
    posts = db.relationship('Post', backref=db.backref('author', lazy=True))

    # Foreign Key: User and User, many to many. Use to subscribe members.
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy=True),
        lazy=True
    )

    # Foreign Key: User and Client, one to many.
    clients = db.relationship('Client', backref=db.backref('user', lazy=True))

    # Foreign Key: User and Invoice, one to many
    invoices = db.relationship('Invoice', backref=db.backref('belongs_to', lazy=True))

    def __repr__(self):
        return '<User %r>' % self.username

    def generate_reset_token(self):
        return jwt.encode({'id':self.id}, current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def check_reset_token(token):
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms='HS256')
            return User.query.filter_by(id=data['id']).first()
        except:
            return 
    
    def is_following(self, user):
       return user in self.followed

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now(TZ_TAIPEI))

    # Foreign Key: Post and User, many to one.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        return '<Post {}>'.format(self.body)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tax_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(140), nullable=False)
    code_number = db.Column(db.Integer, default=9999)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now(TZ_TAIPEI))

    #Foreign Key: Client and User, many to one
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        return '<Client {}, tax ID {}>'.format(self.name, self.tax_number)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rec_id = db.Column(db.String(11), nullable=False, default='default')
    buy_tax_number = db.Column(db.String(8), nullable=False, default='default')
    sell_tax_number = db.Column(db.String(8), nullable=False, default='default')
    time = db.Column(db.DateTime, default=datetime.datetime.now(TZ_TAIPEI))
    price = db.Column(db.String(30), nullable=False, default='default')
    path = db.Column(db.String(150), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now(TZ_TAIPEI))

    #Foreign Key: Invoice and User, many to one
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        if self.rec_id != 'default':
            return '<Invoice {} id {}>'.format(os.path.basename(self.path), self.rec_id)
        else:
            return '<Unreconized Invoice {}>'.format(os.path.basename(self.path))
