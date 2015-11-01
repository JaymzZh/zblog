#!/usr/bin/env python
# encoding:utf-8

from datetime import datetime
import hashlib
import string

from flask.ext.login import UserMixin, AnonymousUserMixin
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
from markdown import markdown
import bleach
import pinyin

from app import db, login_manager
from app.exceptions import ValidationError

__author__ = 'zhangmm'


class PostTags(db.Model):
    __tablename__ = 'post_tag'
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)

    @staticmethod
    def generate_fake(count=50):
        from random import seed, randint

        seed()
        tag_count = Tag.query.count()
        post_count = Post.query.count()
        for i in range(count):
            try:
                t = PostTags(tag_id=randint(1, tag_count - 1),
                             post_id=randint(1, post_count - 1))
                db.session.add(t)
                db.session.commit()
            except:
                db.session.rollback()

    __table_args__ = (UniqueConstraint('tag_id', 'post_id'),)


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))

    posts = db.relationship('PostTags', foreign_keys=[PostTags.tag_id],
                            backref=db.backref('posts', lazy='joined'), lazy='dynamic',
                            cascade='all, delete-orphan')

    @staticmethod
    def generate_fake(count=10):
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            t = Tag(name=forgery_py.internet.first_name())
            db.session.add(t)
            db.session.commit()

    def __repr__(self):
        return '<Tag %r>' % self.name


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    url_title = db.Column(db.String(64), index=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    post_tags = db.relationship('PostTags', foreign_keys=[PostTags.post_id],
                                backref=db.backref('tags', lazy='joined'), lazy='dynamic',
                                cascade='all, delete-orphan')

    @property
    def tags(self):
        return Tag.query.join(PostTags, PostTags.tag_id == Tag.id).filter(PostTags.post_id == self.id)

    @property
    def summary(self):
        if self.body_html:
            return self.body_html[0:300]
        if self.body:
            return self.body[0:300]
        return 'possible no content!'

    @staticmethod
    def on_change_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))

    @staticmethod
    def on_change_title(target, value, oldvalue, initiator):
        target.url_title = pinyin.get(value).replace(' ', '-').lower()

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(title=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id, _external=True)
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)

    def __repr__(self):
        return '<Post %r>' % self.title


db.event.listen(Post.body, 'set', Post.on_change_body)
db.event.listen(Post.title, 'set', Post.on_change_title)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text)
    about_me_html = db.Column(db.Text)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))

    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    @staticmethod
    def on_change_about_me(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.about_me_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=avatar_hash, size=size,
                                                                     default=default, rating=rating)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    @staticmethod
    def generate_fake():
        u = User(email='zhangmin6105@qq.com', username='Jeffiy', password='123456')
        db.session.add(u)
        db.session.commit()

    def to_json(self):
        json_user = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user

    def __repr__(self):
        return '<User %r>' % self.username


db.event.listen(User.about_me, 'set', User.on_change_about_me)


class AnonymousUser(AnonymousUserMixin):
    pass


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
