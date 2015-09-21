# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask

from .views import create_routes, init_blueprint


def create_blueprint(env):
    lang_blueprint = flask.Blueprint('lang', __name__)
    init_blueprint(lang_blueprint, env)
    create_routes().register(lang_blueprint, env)
    return lang_blueprint

