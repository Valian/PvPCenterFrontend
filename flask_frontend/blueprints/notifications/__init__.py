# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask

from .views import create_routes, init_blueprint


def create_blueprint(env):
    notifications_blueprint = flask.Blueprint('notifications', __name__, template_folder='templates')
    create_routes().register(notifications_blueprint, env)
    init_blueprint(notifications_blueprint, env)
    return notifications_blueprint
