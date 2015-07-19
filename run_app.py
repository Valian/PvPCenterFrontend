# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from werkzeug.serving import run_simple
from flask_frontend.app import create_app
from flask_frontend.config import get_local_config

if __name__ == '__main__':
    app = create_app(get_local_config())
    run_simple('localhost', 5000, app, use_reloader=True, use_debugger=True, use_evalex=True)
