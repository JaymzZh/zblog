#!/usr/bin/env python
# encoding:utf-8

from flask import Blueprint

__author__ = 'zhangmm'

auth = Blueprint('auth', __name__)

from app.auth import views
