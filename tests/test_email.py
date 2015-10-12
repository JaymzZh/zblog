#!/usr/bin/env python
# encoding:utf-8

import os
import unittest

from app.models import User
from app.email import send_email

__author__ = 'zhangmm'


class test_email(unittest.TestCase):
    def test_send_email(self):
        self.assertTrue(os.environ.get('MAIL_USERNAME'))
        self.assertTrue(os.environ.get('MAIL_PASSWORD'))
        user = User(id=1, username='jeffiy', email='zhangmin6105@qq.com')
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
