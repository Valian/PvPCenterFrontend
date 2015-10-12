# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask
from flask.ext.frontend.common.views.module import AppModule

from .views import create_routes


def create_blueprint(env):
    """
    :type env: flask_frontend.common.view_helpers.core.ViewEnvironment
    """
    return AppModule(__name__, create_routes(), 'templates')




