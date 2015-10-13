#!/usr/bin/env python
# encoding:utf-8

from threading import Thread

__author__ = 'zhangmm'


def async(fun):
    def wrapper(*args, **kwargs):
        thr = Thread(target=fun, args=args, kwargs=kwargs)
        thr.start()

    return wrapper
