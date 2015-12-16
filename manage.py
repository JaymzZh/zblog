#!/usr/bin/env python
# encoding:utf-8

import os

from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

from app import create_app, db
from app.models import User, Post, Tag, PostTags

__author__ = 'zhangmm'

COV = None
if os.environ.get('ZBLOG_COVERAGE'):
    import coverage

    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

app = create_app(os.getenv('ZBLOG_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Post=Post, Tag=Tag, PostTags=PostTags)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """Run the unit tests"""
    if coverage and os.environ.get('ZBLOG_COVERAGE'):
        import sys
        os.environ['ZBLOG_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'temp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://{0!s}/index.html'.format(covdir))
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profile"""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """Run deployment tasks"""
    from flask.ext.migrate import upgrade

    # upgrade database
    upgrade()


if __name__ == '__main__':
    manager.run()
