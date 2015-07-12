# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask_login
import flask
from flask_frontend.common.api_helper import ApiBlueprint

auth_blueprint = ApiBlueprint('auth', __name__)


@auth_blueprint.record_once
def init(state):
    app = state.app
    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return auth_blueprint.api.get_user(user_id)


@auth_blueprint.before_request
def before_request():
    flask.g.user = flask_login.current_user


@auth_blueprint.route("/login", methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return flask.render_template("auth/login.html")
    else:
        user = auth_blueprint.api.get_user(1)
        flask_login.login_user(user, True)
        return flask.render_template("auth/login.html")

@auth_blueprint.route("/logout", methods=['POST'])
def logout():
    if flask_login.current_user.is_authenticated():
        flask_login.logout_user()
        flask.flash()
