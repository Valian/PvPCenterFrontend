# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import urlparse

import cloudinary
import flask
from flask_babel import gettext
from api.constants import NATIONALITIES
from api.models import SEX


def create_filters(app):
    app.jinja_env.globals['url_for_other_page'] = url_for_other_page
    app.jinja_env.filters['id_to_label'] = id_to_label
    app.jinja_env.filters['country_name'] = code_to_country
    app.jinja_env.filters['cloudinary'] = cloudinary_converter
    app.jinja_env.filters['sex'] = sex_to_text


def url_for_other_page(page):
    args = flask.request.view_args.copy()
    args.update(flask.request.args)
    args['page'] = page
    if '_pjax' in args:
        del args['_pjax']
    return flask.url_for(flask.request.endpoint, **args)


def id_to_label(text):
    """
    :param text: str
    """
    return text.capitalize().replace('-', ' ').replace('_', ' ')


def code_to_country(code):
    return NATIONALITIES.CODE_TO_NATIONALITY.get(code, gettext('Unknown country'))


def cloudinary_converter(url, **kwargs):
    path = urlparse.urlsplit(url).path
    public_id = path.split('/')[-1].split('.')[0]
    return cloudinary.CloudinaryImage(public_id).build_url(**kwargs)


def sex_to_text(value):
    if value == SEX.MALE:
        return gettext('Male')
    if value == SEX.FEMALE:
        return gettext('Female')
    return gettext('Not specified')
