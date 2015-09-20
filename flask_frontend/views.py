# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask


def create_main_views(app):
    """
    :type app: flask.Flask
    """

    @app.errorhandler(403)
    def page_not_found(e):
        return flask.render_template('403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return flask.render_template('404.html'), 404

    @app.errorhandler(422)
    def internal_server_error(e):
        return flask.render_template('422.html'), 500

    @app.errorhandler(500)
    def internal_server_error(e):
        return flask.render_template('500.html'), 500

    @app.route('/')
    @app.route('/index.html')
    def index():
        return flask.render_template('index.html')
