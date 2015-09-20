# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask_frontend.common.api_helper import ApiBlueprint
from .views import create_routes

def create_blueprint(env):
    """
    :type env: flask_frontend.common.view.ViewEnvironment
    """
    teams_blueprint = ApiBlueprint('teams', __name__, template_folder='templates')
    routes = create_routes(env)
    routes.register(teams_blueprint, env)
    return teams_blueprint



