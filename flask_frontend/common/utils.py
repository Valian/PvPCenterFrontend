# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask import Blueprint
import flask


def render_pjax(base, view, **kwargs):
    is_pijax = "X-PJAX" in flask.request.headers
    return flask.render_template('pjax_wrapper.html', is_pjax=is_pijax, extends=base, view=view, **kwargs)

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


from math import ceil


class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, l_edge=2, l_current=2, r_current=5, r_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= l_edge or self.page - l_current - 1 < num < self.page + r_current or num > self.pages - r_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

