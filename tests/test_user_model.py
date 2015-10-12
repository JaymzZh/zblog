#!/usr/bin/env python
# encoding:utf-8

import unittest

from app.models import User

__author__ = 'zhangmm'


class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        """Test user password is hashed"""
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        """Test getting user password is raise an AttributeError"""
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        """Test password verification functions is working proper"""
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        """Test salts of password is random"""
        u1 = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u1.password_hash != u2.password_hash)

    def test_generate_token_is_not_None(self):
        """Test generate confirm token is not none"""
        u = User(id=1)
        self.assertIsNotNone(u.generate_confirmation_token())

    def test_generate_token_confirm(self):
        """Test generate token confirm depends on id of User"""
        u1 = User(id=1)
        u2 = User(id=2)
        token1 = u1.generate_confirmation_token()
        token2 = u2.generate_confirmation_token()
        self.assertTrue(token1 != token2)
