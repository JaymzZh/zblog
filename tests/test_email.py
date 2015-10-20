#!/usr/bin/env python
# encoding:utf-8

import os
import unittest

from app import create_app, db
from app.models import User
from app.email import send_email

__author__ = 'zhangmm'


class TestEmail(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_send_email(self):
        self.assertIsNotNone(os.environ.get('MAIL_USERNAME'))
        self.assertIsNotNone(os.environ.get('MAIL_PASSWORD'))
        user = User(email='zhangmin6105@qq.com')
        token = user.generate_confirmation_token()
        self.assertIsNotNone(send_email(user.email, 'Confirm Your Account',
                                        'auth/email/confirm', user=user, token=token))
