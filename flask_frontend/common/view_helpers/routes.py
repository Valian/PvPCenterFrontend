# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)


class UrlRoute(object):

    def __init__(self, route, view, **kwargs):
        self.view = view
        self.route = route
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
            app.add_url_rule(route.route, view_func=route.view.as_view(env), **route.kwargs)