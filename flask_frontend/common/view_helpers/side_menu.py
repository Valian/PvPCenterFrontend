# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from functools import wraps
from werkzeug.exceptions import HTTPException

from flask.ext.frontend.common.view_helpers.contexts import ContextCreator


def check_auth_exceptions(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
            return True
        except HTTPException:
            return False
    return wrapper


   ###         ###
  #   #       #   #
 #      #   #      #
 #        #        #
 #                 #
  #               #
    #           #
      #       #
        #   #
          #



class MenuEntry(object):

    def __init__(self, url, elem_id, name):
        """
        :type url: str
        :type elem_id: str
        :type name: str
        """
        self.url = url
        self.id = elem_id
        self.name = name


class SideMenuBuilder(ContextCreator):

    def __init__(self):
        self.conditions = {}
        self.links = []
    
    def add_menu_entry(self, link, conditions=None):
        """
        :type link: MenuEntry
        :type conditions: list[str] | None
        """
        self.links.append((link, conditions))

    def add_condition(self, name, condition_func):
        """
        :type name: str
        :type condition_func: (*args, **kwargs) -> raise HTTPException or not
        """
        self.conditions[name] = check_auth_exceptions(condition_func)

    def create_context(self, env, **kwargs):
        condition_statuses = {name: condition(**kwargs) for name, condition in self.conditions.iteritems()}
        menu = []
        for menu_entry, conditions in self.links:
            if all((condition_statuses.get(condition) for condition in conditions)):
                menu.append(menu_entry)
        return dict(side_menu=menu)