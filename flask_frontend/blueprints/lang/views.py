# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask
from flask.ext.babel import get_locale
from flask.ext.frontend.common.view import UrlRoutes, UrlRoute, BaseView

from flask_frontend.blueprints.lang.languages import init_babel, set_locale
from flask_frontend.config import keys


def create_routes():
    return UrlRoutes([
        UrlRoute('/<string:locale>', BaseView(view_func=change_language))
    ])


def init_blueprint(blueprint, env):

    @blueprint.record_once
    def on_register(state):
        app = state.app
        init_babel(app, env)

    @blueprint.before_app_request
    def before_request():
        flask.g.languages = env.config[keys.LANGUAGES]
        flask.g.current_language = get_locale()


def change_language(env, locale):
    if locale in env.config[keys.LANGUAGES]:
        set_locale(locale)
    return flask.redirect(flask.url_for('index'))
