# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask

from flask.ext.frontend.blueprints.lang.languages import init_babel, set_locale, get_locale
from flask_frontend.config import keys
from . import lang_blueprint


@lang_blueprint.record_once
def on_register(state):
    app = state.app
    init_babel(app)


@lang_blueprint.before_app_request
def before_request():
    flask.g.languages = lang_blueprint.config[keys.LANGUAGES]
    flask.g.current_language = get_locale()


@lang_blueprint.route('/<string:locale>')
def change_language(locale):
    if locale in lang_blueprint.config[keys.LANGUAGES]:
        set_locale(locale)
    return flask.redirect(flask.url_for('index'))
