#!/usr/bin/env python
# encoding:utf-8

from flask import Blueprint

__author__ = 'zhangmm'

api = Blueprint('api', __name__)

from app.api_1_0 import authentication, posts, users, errors
