# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask_login
import flask

from .forms import LoginForm, RegisterForm
from .user import User
from . import auth_blueprint


@auth_blueprint.record_once
def init(state):
    app = state.app
    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        token = flask.session.get('token')
        if not token:
            return None

        response = auth_blueprint.api.users.get_single(user_id, model=User)
        if response.ok:
            user = response.data
            user.token = token
            return user
        return None


@auth_blueprint.before_app_request
def before_app_request():
    flask.g.login_form = LoginForm(auth_blueprint.api)


@auth_blueprint.route("/login", methods=['GET', 'POST'])
def login():
    form = flask.g.login_form
    if form.validate_on_submit():
        flask_login.login_user(form.result, remember=form.remember_me.data)
        flask.session['token'] = form.result.token
        return form.redirect(flask.url_for('index'))

    return flask.render_template("login.html", form=form)


@auth_blueprint.route("/logout", methods=['POST'])
def logout():
    if flask_login.current_user.is_authenticated():
        flask_login.logout_user()
    return flask.redirect(flask.url_for('auth.login'))


@auth_blueprint.route("/register", methods=['POST', 'GET'])
def register():
    register_form = RegisterForm(auth_blueprint.api)
    if register_form.validate_on_submit():
        flask_login.login_user(register_form.result)
        return flask.redirect(flask.url_for('index'))

    return flask.render_template("register.html", form=register_form)
