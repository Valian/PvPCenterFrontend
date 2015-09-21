# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask

from .views import init_blueprint, create_routes


def create_blueprint(env):
    auth_blueprint = flask.Blueprint('auth', __name__, template_folder='templates')
    create_routes().register(auth_blueprint, env)
    init_blueprint(auth_blueprint, env)
    return auth_blueprint
