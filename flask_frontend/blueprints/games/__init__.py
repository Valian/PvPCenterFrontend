# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask_frontend.common.api_helper import ApiBlueprint
from .views import create_routes

def create_blueprint(env):
    games_blueprint = ApiBlueprint('games', __name__, template_folder='templates')
    routes = create_routes(env)
    routes.register(games_blueprint)
