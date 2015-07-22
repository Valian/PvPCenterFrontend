# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask.ext.babel import gettext

import flask_login
import flask

from flask_frontend.auth.forms import LoginForm
from flask_frontend.auth.user import User
from flask_frontend.common.api_helper import ApiBlueprint

auth_blueprint = ApiBlueprint('auth', __name__, template_folder='templates')


@auth_blueprint.record_once
def init(state):
    app = state.app
    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return auth_blueprint.api.user.get(user_id, model=User)


@auth_blueprint.before_request
def before_app_request():
    flask.g.user = flask_login.current_user


@auth_blueprint.route("/login", methods=['GET', 'POST'])
def login():
    login_form = LoginForm(auth_blueprint.api)
    if login_form.validate_on_submit():
        flask_login.login_user(login_form.user)
        return flask.redirect(flask.url_for('index'))

    flask.flash(gettext('Unable to login'), category='error')
    return flask.render_template("login.html", form=login_form)


@auth_blueprint.route("/logout", methods=['POST'])
def logout():
    if flask_login.current_user.is_authenticated():
        flask_login.logout_user()
        flask.flash()
