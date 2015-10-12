# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask.helpers import _PackageBoundObject
from jinja2 import ChoiceLoader


class AppModule(_PackageBoundObject):

    def __init__(self, import_name, routes, template_folder):
        """
        :type import_name: str
        :type routes: flask_frontend.common.view_helpers.routes.UrlRoutes
        :type template_folder:
        """
        super(AppModule, self).__init__(import_name, template_folder)
        self.routes = routes

    def register(self, app, env):
        """
        :type app: flask.Flask
        """
        self.routes.register(app, env)
        app.jinja_loader = ChoiceLoader([
            self.jinja_loader,
            app.jinja_loader
        ])

