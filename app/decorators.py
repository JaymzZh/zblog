#!/usr/bin/env python
# encoding:utf-8

from threading import Thread
from functools import wraps

from flask import abort
from flask.ext.login import current_user
from app.models import Permission

__author__ = 'zhangmm'


def async(fun):
    def wrapper(*args, **kwargs):
        thr = Thread(target=fun, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
