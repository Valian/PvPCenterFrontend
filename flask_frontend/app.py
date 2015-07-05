import logging
from flask import Flask
from flask_assets import Environment, Bundle
from flask_frontend.config import get_config


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())
    app.static_folder = app.config.get('STATIC_FOLDER')
    return app


def create_logger(app):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if not app.debug:
        stderr_handler = logging.StreamHandler()
        stderr_handler.setLevel(logging.INFO)
        logger.addHandler(stderr_handler)

    return logger

def create_bundles(app):
    assets = Environment(app)
    static = '../static/'
    bower = '../../bower_components/'
    js = Bundle(static + 'javascripts/*.coffee', filters=['coffeescript', 'rjsmin'], output='main.min.js')
    libs = Bundle(bower + '*/dist/*.min.js', bower + 'owlcar/owl-carousel/*.min.js', output='libs.min.js')
    less = Bundle(static + 'stylesheets/*.less', filters=['less'], output='styles.css')
    css_libs = Bundle(bower + '*/dist/*.css', bower + 'owlcar/owl-carousel/*.css', output='lib_styles.css')
    assets.register('main_js', js)
    assets.register('libs_js', libs)
    assets.register('css', less)
    assets.register('libs_css', css_libs)

app = create_app()
create_bundles(app)
logger = create_logger(app)

from flask_frontend.views import *
