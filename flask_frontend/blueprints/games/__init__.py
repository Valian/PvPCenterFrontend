# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask_frontend.common.api_helper import ApiBlueprint

games_blueprint = ApiBlueprint('games', __name__, template_folder='templates')

from .views import *
