# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask_frontend.common.api_helper import ApiBlueprint

users_blueprint = ApiBlueprint('users', __name__, template_folder='templates')

from .views import *
