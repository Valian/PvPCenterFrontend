# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask_frontend.common.api_helper import ApiBlueprint

auth_blueprint = ApiBlueprint('auth', __name__, template_folder='templates')

from .views import *
