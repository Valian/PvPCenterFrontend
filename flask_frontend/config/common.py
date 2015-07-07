# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import os


class CommonConfig(object):
    SITE_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    STATIC_FOLDER = 'dist'

    BACKEND_URL = 'url'
    BACKEND_LOGIN = 'login'
    BACKEND_PASS = 'pass'
