# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
from flask import url_for
import re

from werkzeug.exceptions import HTTPException

from flask_frontend.common.view_helpers.contexts import ContextCreator
from flask_frontend.common.view_helpers.restrictions import RestrictionRegistry


def check_restriction(f, *args, **kwargs):
    try:
        f(*args, **kwargs)
        return True
    except HTTPException:
        return False


class MenuEntry(object):

    __slots__ = ['_url_constructor', 'url', 'text', 'restrictions']

    def __init__(self, url_constructor, text, restrictions=None):
        """
        :type url_constructor: UrlConstructor | None
        :type text: str
        :type restrictions: tuple[str] | None
        """
        self._url_constructor = url_constructor
        self.text = text
        self.url = '#'
        self.restrictions = restrictions or []

    def update_url(self, kwargs):
        if self._url_constructor:
            self.url = self._url_constructor.create_url(kwargs)
        else:
            self.url = '#'


class UrlConstructor(object):

    def __init__(self, endpoint, *args):
        self.endpoint = endpoint
        self.required_args = args

    def create_url(self, kwargs):
        try:
            url_kwargs = {name: kwargs[name] for name in self.required_args}
            return url_for(self.endpoint, **url_kwargs)
        except KeyError as e:
            raise ValueError('Unable to create url for endpoint {0} using kwargs {1}, missing: {2}'.format(
                self.endpoint, kwargs, e))


class SideMenu(object):

    def __init__(self):
        self.entries = []
        self.restrictions = set()

    def add_entry(self, url_constructor, text, *restrictions):
        self.restrictions.update(restrictions)
        entry = MenuEntry(url_constructor, text, restrictions)
        self.entries.append(entry)

    def generate(self, env, kwargs):
        restriction_statuses = RestrictionRegistry.get_restrictions_statuses(self.restrictions, env, kwargs)
        menu = []
        for menu_entry in self.entries:
            if all((restriction_statuses.get(restriction) for restriction in menu_entry.restrictions)):
                menu_entry.update_url(kwargs)
                menu.append(menu_entry)
        return menu


class SideMenuContext(ContextCreator):

    def __init__(self):
        self.menu = SideMenu()
        self.init_menu(self.menu)

    def init_menu(self, menu):
        pass

    def create_context(self, env, **kwargs):
        generated_menu = self.menu.generate(env, kwargs)
        return dict(side_menu=generated_menu)
