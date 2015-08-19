# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from functools import wraps

import flask
import flask_login


def only_current_user(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = flask_login.current_user
        if not user or user.id != kwargs.get('user_id', -1):
            flask.abort(403)

        return f(*args, **kwargs)
    return wrapper
