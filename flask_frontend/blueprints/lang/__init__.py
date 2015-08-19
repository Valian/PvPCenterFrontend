# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask_frontend.config import keys
from flask_frontend.common.utils import ConfigBlueprint

lang_blueprint = ConfigBlueprint('lang', __name__, [keys.LANGUAGES])

from .views import *
