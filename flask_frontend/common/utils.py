# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
from functools import wraps
from abc import abstractmethod, ABCMeta

import time
import cloudinary

from flask import Blueprint
import flask
from common.logable import Logable
from flask_frontend.config import keys


class CustomRoute(Logable):

    __metaclass__ = ABCMeta

    def __init__(self, blueprint, prefix):
        self.prefix = prefix
        self.blueprint = blueprint

    def __call__(self, route, **kwargs):

        def decorator(f):
            modified_route = '{0}{1}'.format(self.prefix, route)

            @wraps(f)
            def wrapper(**wrapper_kwargs):
                new_kwargs = self.prepare_view(**wrapper_kwargs)
                return f(**new_kwargs)

            self.blueprint.add_url_rule(modified_route, endpoint=f.__name__, view_func=wrapper, **kwargs)
            return wrapper
        return decorator

    @abstractmethod
    def prepare_view(self, **kwargs):
        """
        :rtype: dict
        """


def generate_cloudinary_options(config, **kwargs):
    timestamp = int(time.time())
    callback = flask.url_for('cloudinary_cors')
    api_key = config[keys.CLOUDINARY_PUBLIC_KEY]
    secret = config[keys.CLOUDINARY_SECRET]
    kwargs.update({'timestamp': timestamp, 'callback': callback})
    return cloudinary.utils.sign_request(kwargs, {'api_key': api_key, 'api_secret': secret})


def render_pjax(base, view, **kwargs):
    is_pijax = "X-PJAX" in flask.request.headers
    return flask.render_template('pjax_wrapper.html', is_pjax=is_pijax, extends=base, view=view, **kwargs)


def first_or_none(iterable):
    return iterable[0] if len(iterable) > 0 else None


class InvalidConfigurationException(Exception):
    def __init__(self, blueprint_name, e):
        super(InvalidConfigurationException, self).__init__(
            "Invalid configuration for blueprint {0}, error: {1}".format(blueprint_name, e))


class ConfigBlueprint(Blueprint):
    def __init__(self, name, import_name, config_keys=None, *args, **kwargs):
        super(ConfigBlueprint, self).__init__(name, import_name, *args, **kwargs)
        self.keys = config_keys or []
        self.config = {}

    def register(self, app, options, first_registration=False):
        try:
            for key in (self.keys or []):
                self.config[key] = app.config[key]
        except KeyError as e:
            raise InvalidConfigurationException(self.name, e)

        super(ConfigBlueprint, self).register(app, options, first_registration)
