#!/usr/bin/env python
# encoding:utf-8

from flask.ext.wtf import Form
from flask.ext.pagedown.fields import PageDownField
from wtforms import StringField, SubmitField, ValidationError, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, Regexp
from app.models import User, Tag

__author__ = 'zhangmm'


class NameForm(Form):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username',
                           validators=[DataRequired(), Length(1, 64),
                                       Regexp('^[A-Za-z0-9][A-Za-z0-9_.]*$', 0,
                                              'Username must have only letters number, dots and underscores')])
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = PageDownField('About me', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate_email(self, field):
        email = field.data
        if email != self.user.email and \
                User.query.filter_by(email=email).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        username = field.data
        if username != self.user.username and \
                User.query.filter_by(username=username).first():
            raise ValidationError('Username already in use.')


class PostForm(Form):
    title = StringField('Title', validators=[DataRequired()])
    tags = SelectMultipleField('Tags', coerce=int)
    body = PageDownField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.tags.choices = [(tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()]


class TagForm(Form):
    name = StringField('Tag name')
    submit = SubmitField('Submit')
