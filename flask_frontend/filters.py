# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask


def create_filters(app):
    app.jinja_env.globals['url_for_other_page'] = url_for_other_page
    app.jinja_env.filters['id_to_label'] = id_to_label


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


