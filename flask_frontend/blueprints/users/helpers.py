# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask_login


def only_current_user(*args, **kwargs):
    logged_user = flask_login.current_user
    user_id = kwargs.get('user_id')
    if user_id is None:
        user_id = kwargs['user'].id
    if not logged_user.is_authenticated() or logged_user.id != user_id:
        raise EnvironmentError('No user or user_id in view params')
