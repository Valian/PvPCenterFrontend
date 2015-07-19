import logging

from flask import Flask
from flask_assets import Environment, Bundle
from flask_frontend.views import create_main_views
from flask_frontend.config import keys
from flask_frontend.auth.views import auth_blueprint
from flask_frontend.lang.views import lang_blueprint


def create_app(config=None):
    app = Flask(__name__)
    config = config or {}
    app.config.update(config)
    app.static_folder = app.config.get(keys.STATIC_FOLDER)

    app.register_blueprint(lang_blueprint)
    app.register_blueprint(auth_blueprint)

    create_logger(app)
    create_bundles(app)
    create_main_views(app)

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
    js = Bundle(
        static + 'javascripts/*.coffee',
        filters=['coffeescript', 'rjsmin'], output='js/main.min.js')
    libs = Bundle(
        bower + 'jquery/dist/jquery.min.js',
        bower + '*/dist/**/*.min.js',
        bower + 'owlcar/owl-carousel/*.min.js',
        output='js/libs.min.js')
    less = Bundle(
        static + 'stylesheets/*.less',
        filters=['less'], output='stylesheets/styles.css')
    css_libs = Bundle(
        bower + 'bootstrap/dist/css/bootstrap.css',
        bower + 'bootstrap/dist/css/bootstrap-theme.css',
        bower + 'components-font-awesome/css/font-awesome.css',
        bower + 'flag-icon-css/css/flag-icon.css',
        bower + 'owlcar/owl-carousel/*.min.css',
        output='stylesheets/lib_styles.css')
    assets.register('main_js', js)
    assets.register('libs_js', libs)
    assets.register('css', less)
    assets.register('libs_css', css_libs)
