# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)


class UrlRoute(object):

    def __init__(self, route, view, **kwargs):
        """
        :type route: str
        :type view: flask_frontend.common.views.core.View
        :type menu:
        """
        self.view = view
        self.route = route


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
            view_class = route.view
            view_func = view_class.as_view(env)
            endpoint = view_class.get_endpoint()
            app.add_url_rule(route.route, view_func=view_func, endpoint=endpoint)
