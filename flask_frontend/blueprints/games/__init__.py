# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask_frontend.common.api_helper import ApiBlueprint
from .views import create_routes, init_blueprint


def create_blueprint(env):
    games_blueprint = ApiBlueprint('games', __name__, template_folder='templates')
    init_blueprint(games_blueprint, env)
    create_routes().register(games_blueprint, env)
    return games_blueprint
