# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask_frontend.common.api_helper import ApiBlueprint
from .views import init_blueprint, create_routes

def create_blueprint(env):
    auth_blueprint = ApiBlueprint('auth', __name__, template_folder='templates')
    routes = create_routes(env)
    routes.register(auth_blueprint, env)
    init_blueprint(auth_blueprint, env)
    return auth_blueprint
