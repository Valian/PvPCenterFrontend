# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask_frontend.config import keys
from flask_frontend.common.utils import ConfigBlueprint
from .views import create_routes, init_blueprint


def create_blueprint(env):
    lang_blueprint = ConfigBlueprint('lang', __name__, [keys.LANGUAGES])
    init_blueprint(lang_blueprint, env)
    create_routes().register(lang_blueprint, env)
    return lang_blueprint

