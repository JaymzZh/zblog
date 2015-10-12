#!/usr/bin/env python
# encoding:utf-8

from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, login_required, logout_user

from . import auth
from ..models import User
from .forms import LoginForm

from . import auth
from .forms import LoginForm

__author__ = 'zhangmm'

@auth.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user is not None and user.verify_password(login_form.password.data):
            login_user(user, login_form.remember_me.data)
            return redirect(request.args.get('next')) or url_for('main.index')
        flash('Invalid username or password.')
    return render_template('auth/login.html', form = login_form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
