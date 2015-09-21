# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
from functools import wraps
import inspect
from abc import abstractmethod, ABCMeta

import time
import cloudinary

from flask import Blueprint
import flask
from werkzeug.exceptions import HTTPException
from common.logable import Logable
from flask_frontend.config import keys


def restrict(checker):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                checker(*args, **kwargs)
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise
                flask.abort(500)
            return f(*args, **kwargs)
        return wrapper
    return decorator


def pjax(template, pjax_block='pjax_content', **kwargs):
    if "X-PJAX" in flask.request.headers:
        app = flask.current_app
        app.update_template_context(kwargs)
        template = app.jinja_env.get_template(template)
        block = template.blocks[pjax_block]
        context = template.new_context(kwargs)
        return u''.join(block(context))
    else:
        return flask.render_template(template, **kwargs)


def first_or_none(iterable):
    return iterable[0] if len(iterable) > 0 else None


def get_true_argspec(method):
    """taken from flask.classy extension"""

    argspec = inspect.getargspec(method)
    args = argspec[0]
    if args:
        return argspec
    if hasattr(method, '__func__'):
        method = method.__func__
    if not hasattr(method, '__closure__') or method.__closure__ is None:
        return argspec

    closure = method.__closure__
    for cell in closure:
        inner_method = cell.cell_contents
        if inner_method is method:
            continue
        try:
            true_argspec = get_true_argspec(inner_method)
            if true_argspec and true_argspec.args:
                return true_argspec
        except TypeError:
            # not a callable cell
            continue

    return argspec


class DecoratorCompatibilityError(Exception):
    pass
