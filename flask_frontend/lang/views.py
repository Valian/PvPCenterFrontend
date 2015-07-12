# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask

from flask_frontend.lang.languages import init_babel, set_locale, set_timezone

from flask_frontend.common.utils import ConfigBlueprint
from flask_frontend.config import keys

lang_blueprint = ConfigBlueprint('lang', __name__, [keys.LANGUAGES])

@lang_blueprint.record_once
def on_register(state):
    app = state.app
    init_babel(app)


@lang_blueprint.before_app_request
def before_request():
    flask.g.languages = lang_blueprint.config[keys.LANGUAGES]


@lang_blueprint.route('/lang/<string:locale>')
def change_language(locale):
    if locale in lang_blueprint.config[keys.LANGUAGES]:
        set_locale(locale)
    return flask.redirect(flask.url_for('index'))
