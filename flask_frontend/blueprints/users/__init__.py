# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
from flask_frontend.config import keys

from flask_frontend.common.api_helper import ApiBlueprint

users_blueprint = ApiBlueprint(
    'users', __name__, template_folder='templates', config_keys=[keys.CLOUDINARY_SECRET, keys.CLOUDINARY_PUBLIC_KEY])

from .views import *
