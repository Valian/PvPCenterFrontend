import logging

from flask import Flask

from flask_frontend.views import create_main_views
from flask_frontend.bundles import create_bundles
from flask_frontend.config import keys
from flask_frontend.blueprints.games import games_blueprint
from flask_frontend.blueprints.auth import auth_blueprint
from flask_frontend.blueprints.lang.views import lang_blueprint
from flask_frontend.blueprints.users import users_blueprint
from flask_frontend.blueprints.notifications import notifications_blueprint
from flask_frontend.blueprints.teams import teams_blueprint


def create_app(config=None):
    app = Flask(__name__)
    config = config or {}
    app.config.update(config)
    app.static_folder = app.config.get(keys.STATIC_FOLDER)

    app.register_blueprint(lang_blueprint, url_prefix='/lang')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(users_blueprint, url_prefix='/users')
    app.register_blueprint(games_blueprint, url_prefix='/games')
    app.register_blueprint(teams_blueprint, url_prefix='/teams')
    app.register_blueprint(notifications_blueprint, url_prefix='/notifications')

    create_logger(app)
    create_bundles(app)
    create_main_views(app)

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

