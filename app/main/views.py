#!/usr/bin/env python
# encoding:utf-8

from datetime import datetime

from flask import render_template, session, redirect, url_for

from . import main
from .forms import NameForm
from .. import db
from ..models import User, Role

__author__ = 'zhangmm'


@main.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())


@main.route('/user', methods=['GET', 'POST'])
def user():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session["known"] = False
        else:
            session["known"] = True
        session["name"] = form.name.data
        form.name.data = ""
        return redirect(url_for('user'))
    return render_template('user.html', form=form, name=session.get('name'), known=session.get('known', False))
