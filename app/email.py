#!/usr/bin/env python
# encoding:utf-8

import os
from threading import Thread

from flask import render_template
from flask.ext.mail import Message

from app import create_app
from . import mail

__author__ = 'zhangmm'

app = create_app(os.getenv('ZBLOG_CONFIG') or 'default')


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['ZBLOG_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['ZBLOG_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
