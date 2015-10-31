#!/usr/bin/env python
# encoding:utf-8

from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, login_required, logout_user, current_user

from app.auth import auth
from app.models import db, User
from app.auth.forms import LoginForm, ChangePwdForm

__author__ = 'zhangmm'


@auth.route('/admin-login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_app_request():
    if current_user.is_authenticated:
        current_user.ping()


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePwdForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            logout_user()
            flash('Your password has been changed, please login again.')
            return redirect(url_for('auth.login'))
        else:
            flash('Your old password is incorrect.')
    return render_template('auth/change_password.html', form=form)
