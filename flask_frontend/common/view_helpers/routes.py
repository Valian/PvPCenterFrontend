# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)


class UrlRoute(object):

    def __init__(self, route, view, restrict=None, menu=None, **kwargs):
        self.menu = menu
        self.view = view
        self.route = route
        self.restrict = restrict or []
        self.kwargs = kwargs


class UrlRoutes(object):

    def __init__(self, routes):
        """
        :type routes: list[UrlRoute]
        :return:
        """
        self.routes = routes

    def register(self, app, env):
        """
        :type app: flask.Flask | flask.Blueprint
        :type env: ViewEnvironment
        """
        for route in self.routes:
            """:type : UrlRoute"""
            view_func = route.view.as_view(env, restrictions=route.restrict, menu=route.menu)
            app.add_url_rule(route.route, view_func=view_func, **route.kwargs)
