#!/usr/bin/env python
# encoding:utf-8

from threading import Thread
from functools import wraps

from flask import abort
from flask.ext.login import current_user

__author__ = 'zhangmm'


def async(fun):
    def wrapper(*args, **kwargs):
        thr = Thread(target=fun, args=args, kwargs=kwargs)
        thr.start()

    return wrapper
