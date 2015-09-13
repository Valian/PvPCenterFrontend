# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from functools import wraps

import flask
import flask_login


def only_current_user(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        logged_user = flask_login.current_user
        try:
            user_id = kwargs.get('user_id') or kwargs.get('user').id
            if not logged_user.is_authenticated() or logged_user.id != user_id:
                flask.abort(403)
        except Exception:
            flask.abort(500)

        return f(*args, **kwargs)
    return wrapper
