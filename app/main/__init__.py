#!/usr/bin/env python
# encoding:utf-8

from flask import Blueprint

from app.models import Permission

__author__ = 'zhangmm'

main = Blueprint('main', __name__)

from . import views, errors


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
