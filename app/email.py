#!/usr/bin/env python
# encoding:utf-8

from flask import current_app, render_template
from flask.ext.mail import Message

from app import mail
from app.decorators import async

__author__ = 'zhangmm'


@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['ZBLOG_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['ZBLOG_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    send_async_email(app, msg)
