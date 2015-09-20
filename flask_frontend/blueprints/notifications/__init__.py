# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask_frontend.common.api_helper import ApiBlueprint
from .views import create_routes


def create_blueprint(env):
    notifications_blueprint = ApiBlueprint('notifications', __name__, template_folder='templates')
    create_routes().register(notifications_blueprint, env)
    return notifications_blueprint
