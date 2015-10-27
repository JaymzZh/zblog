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
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USER_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
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

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # send error log to admin'email
        import logging
        from logging.handlers import SMTPHandler

        # log to stderr
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USER_TLS', None):
                secure = ()
            mail_hanlder = SMTPHandler(
                mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
                fromaddr=cls.ZBLOG_MAIL_SENDER,
                toaddrs=[cls.ZBLOG_ADMIN],
                subject=cls.ZBLOG_MAIL_SUBJECT_PREFIX + 'Application Error',
                credentials=credentials,
                secure=secure
            )
            mail_hanlder.setLevel(logging.ERROR)
            app.logger.addHandler(mail_hanlder)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        # log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
