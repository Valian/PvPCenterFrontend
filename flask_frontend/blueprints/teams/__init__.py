# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask

from .views import create_routes


def create_blueprint(env):
    """
    :type env: flask.ext.frontend.common.view_helpers.core.ViewEnvironment
    """
    teams_blueprint = flask.Blueprint('teams', __name__, template_folder='templates')
    create_routes().register(teams_blueprint, env)
    return teams_blueprint



