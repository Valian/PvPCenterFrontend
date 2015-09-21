# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask

from .views import create_routes


def create_blueprint(env):
    users_blueprint = flask.Blueprint('users', __name__, template_folder='templates')
    create_routes().register(users_blueprint, env)
    return users_blueprint
