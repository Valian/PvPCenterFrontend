# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask import session, request
from flask_babel import Babel
from flask_frontend.config import keys

LOCALE = 'locale'
TIMEZONE = 'timezone'

babel = Babel()

def init_babel(app):
    babel.init_app(app)
    babel.locale_selector_func = get_locale
    babel.timezone_selector_func = get_timezone


def set_locale(locale):
    # todo - add support check
    session[LOCALE] = locale


def set_timezone(timezone):
    session[TIMEZONE] = timezone


def get_locale():
    locale = session.get(LOCALE)
    if locale is not None:
        return locale
    return request.accept_languages.best_match(babel.app.config[keys.LANGUAGES].keys())


def get_timezone():
    timezone = session.get(TIMEZONE)
    if timezone is not None:
        return timezone


