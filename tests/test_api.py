#!/usr/bin/env python
# encoding:utf-8

import unittest
import json
import re
from base64 import b64encode

from flask import url_for

from app import create_app, db
from app.models import User, Role, Post, Comment

__author__ = 'zhangmm'


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_404(self):
        response = self.client.get('wrong/url', headers=self.get_api_headers('email', 'password'))
        self.assertTrue(response.status_code == 404)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['error'] == 'not found')

    def test_no_auth(self):
        response = self.client.get(url_for('api.get_token'), content_type='application/json')
        self.assertTrue(response.status_code == 401)

    def test_bad_auth(self):
        # add a user
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='zhangmin6105@qq.com', password='cat', confirmed=True, role=r)
        db.session.add(u)
        db.session.commit()

        # authenticate with bad password
        response = self.client.get(url_for('api.get_posts'), headers=self.get_api_headers('zhangmin6105@qq.com', 'c'))
        self.assertTrue(response.status_code == 401)

    def test_token_auth(self):
        # add a user
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='zhangmin6105@qq.com', password='cat', confirmed=True, role=r)
        db.session.add(u)
        db.session.commit()

        # authenticate with a bad token
        response = self.client.get(url_for('api.get_posts'), headers=self.get_api_headers('bad-token', ''))
        self.assertTrue(response.status_code == 401)

        # get a token
        response = self.client.get(url_for('api.get_token'), headers=self.get_api_headers('zhangmin6105@qq.com', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        # issue a request with the token
        response = self.client.get(url_for('api.get_posts'), headers=self.get_api_headers(token, ''))
        self.assertTrue(response.status_code == 200)

    def test_anonymous(self):
        response = self.client.get(url_for('api.get_posts'), headers=self.get_api_headers('', ''))
        self.assertTrue(response.status_code == 200)

    def test_posts(self):
        # add a user
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='zhangmin6105@qq.com', password='cat', confirmed=True)
        db.session.add(u)
        db.session.commit()

        # write an empty post
        response = self.client.post(url_for('api.new_post'), headers=self.get_api_headers('zhangmin6105@qq.com', 'cat'),
                                    data=json.dumps({'body': ''}))
        self.assertTrue(response.status_code == 400)

        # write a post
        response = self.client.post(url_for('api.new_post'), headers=self.get_api_headers('zhangmin6105@qq.com', 'cat'),
                                    data=json.dumps({'body': 'body of the *zblog* post'}))
        self.assertTrue(response.status_code == 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)

        # get the new post
        response = self.client.get(url, headers=self.get_api_headers('zhangmin6105@qq.com', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['url'] == url)
        self.assertTrue(json_response['body'] == 'body of the *zblog* post')
        self.assertTrue(json_response['body_html'] == '<p>body of the <em>zblog</em> post</p>')
        json_post = json_response

        # get the post from the user
        response = self.client.get(url_for('api.get_user_posts', id=u.id),
                                   headers=self.get_api_headers('zhangmin6105@qq.com', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('posts'))
        self.assertTrue(json_response.get('count', 0) == 1)
        self.assertTrue(json_response['posts'][0] == json_post)

        # edit post
        response = self.client.put(url, headers=self.get_api_headers('zhangmin6105@qq.com', 'cat'),
                                   data=json.dumps({'body': 'updated body'}))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['url'] == url)
        self.assertTrue(json_response['body'] == 'updated body')
        self.assertTrue(json_response['body_html'] == '<p>updated body</p>')

    def test_user(self):
        # add two users
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u1 = User(email='zhangmin6105@qq.com', username='zhangmm', password='cat', confirmed=True, role=r)
        u2 = User(email='zhangmin@qq.com', username='zhangmin', password='cat', confirmed=True, role=r)
        db.session.add_all([u1, u2])
        db.session.commit()

        # get users
        response = self.client.get(url_for('api.get_user', id=u1.id),
                                   headers=self.get_api_headers('zhangmin6105@qq.com', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['username'] == 'zhangmm')
        response = self.client.get(url_for('api.get_user', id=u2.id),
                                   headers=self.get_api_headers('zhangmin@qq.com', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['username'] == 'zhangmin')
