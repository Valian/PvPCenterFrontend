# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask import Blueprint
import flask


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
