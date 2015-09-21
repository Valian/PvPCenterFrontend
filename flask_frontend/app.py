import logging

import cloudinary
from flask import Flask
import flask_gravatar

from flask_frontend.common.api_helper import get_api_instance
from flask.ext.frontend.common.view_helpers.core import ViewEnvironment
from flask_frontend.filters import create_filters
from flask_frontend.views import create_main_views
from flask_frontend.bundles import create_bundles
from flask_frontend.config import keys
from flask_frontend.blueprints import games
from flask_frontend.blueprints import auth
from flask_frontend.blueprints import lang
from flask_frontend.blueprints import users
from flask_frontend.blueprints import notifications
from flask_frontend.blueprints import teams


def create_app(config=None):
    app = Flask(__name__)
    config = config or {}
    app.config.update(config)
    app.static_folder = app.config.get(keys.STATIC_FOLDER)
    app.api = get_api_instance(app.config)

    flask_gravatar.Gravatar(app)

    env = ViewEnvironment(app.api, app.config)
    app.register_blueprint(lang.create_blueprint(env), url_prefix='/lang')
    app.register_blueprint(auth.create_blueprint(env), url_prefix='/auth')
    app.register_blueprint(users.create_blueprint(env), url_prefix='/users')
    app.register_blueprint(games.create_blueprint(env), url_prefix='/games')
    app.register_blueprint(teams.create_blueprint(env), url_prefix='/teams')
    app.register_blueprint(notifications.create_blueprint(env), url_prefix='/notifications')

    create_logger(app)
    create_filters(app)
    create_bundles(app)
    create_main_views(app)
    initialize_cloudinary(app)

    return app


def create_logger(app):
    logger = logging.getLogger()
    level = app.config.get(keys.LOG_LEVEL, 'INFO')
    logger.setLevel(level)
    if not app.debug:
        stderr_handler = logging.StreamHandler()
        stderr_handler.setLevel(level)
        logger.addHandler(stderr_handler)
    return logger


def initialize_cloudinary(app):
    cloudinary.config(
        cloud_name=app.config[keys.CLOUDINARY_CLOUD_NAME],
        api_key=app.config[keys.CLOUDINARY_PUBLIC_KEY],
        api_secret=app.config[keys.CLOUDINARY_SECRET])
