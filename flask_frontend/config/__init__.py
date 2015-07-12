# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
from flask_frontend.config.common import CommonConfig
from flask_frontend.config.local import LocalConfig


def get_config():
    config = dict(CommonConfig)
    config.update(LocalConfig)
    return config
