# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask
from flask_babel import get_locale
from flask_frontend.common.view_helpers.core import BaseView, view
from flask_frontend.common.view_helpers.routes import UrlRoute, UrlRoutes

from flask_frontend.blueprints.lang.languages import init_babel, set_locale
from flask_frontend.config import keys


def create_routes():
    return UrlRoutes([
        UrlRoute('/<string:locale>', change_language)
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


@view()
def change_language(env, locale):
    if locale in env.config[keys.LANGUAGES]:
        set_locale(locale)
    return flask.redirect(flask.url_for('index'))
