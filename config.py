#!/usr/bin/env python
# encoding:utf-8

import os

__author__ = 'zhangmm'

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or 'hard to guess key'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    ZBLOG_MAIL_SUBJECT_PREFIX = '[ZBlog]'
    ZBLOG_MAIL_SENDER = 'zhangmin6105@163.com'
    ZBLOG_ADMIN = os.environ.get('ZBlog_ADMIN') or 'zhangmin6105@163.com'
    ZBLOG_POSTS_PER_PAGE = 20
    ZBLOG_FOLLOWERS_PER_PAGE = 50
    ZBLOG_COMMENTS_PER_PAGE = 30
    SQLALCHEMY_RECORD_QUERIES = True
    ZBLOG_SLOW_DB_QUERY_TIME = 0.5

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USER_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost:5000'
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
