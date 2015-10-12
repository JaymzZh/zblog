#!/usr/bin/env python
# encoding:utf-8

from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, login_required, logout_user, current_user

from . import auth
from ..models import db, User
from .forms import LoginForm, RegistrationForm
from ..email import send_email

__author__ = 'zhangmm'


@auth.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user is not None and user.verify_password(login_form.password.data):
            login_user(user, login_form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=login_form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegistrationForm()
    if register_form.validate_on_submit():
        user = User(email=register_form.email.data, username=register_form.password.data,
                    password=register_form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email..')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=register_form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account.Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_app_request():
    if current_user.is_authenticated and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', current_user=current_user)


@auth.route('/confirm')
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email')
    return redirect(url_for('main.index'))
