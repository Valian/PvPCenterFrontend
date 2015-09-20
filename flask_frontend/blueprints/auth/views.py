# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask_login
import flask

from flask.ext.frontend.common.view import UrlRoutes, template_view, UrlRoute, view
from .forms import LoginForm, RegisterForm


def create_routes():
    return UrlRoutes([
        UrlRoute('/login', login, methods=['GET', 'POST']),
        UrlRoute('/logout', logout, methods=['POST']),
        UrlRoute('/register', register,  methods=['GET', 'POST'])
    ])


def init_blueprint(blueprint, env):

    @blueprint.record_once
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

            response = env.api.users.get_single(user_id)
            if response.ok:
                user = response.data
                user.token = token
                return user
            return None

    @blueprint.before_app_request
    def before_app_request():
        flask.g.login_form = LoginForm(env.api)


@template_view("login.html")
def login():
    form = flask.g.login_form
    if form.validate_on_submit():
        login_user(form.result, form.remember_me.data, form.email.data, form.password.data)
        return form.redirect(flask.url_for('index'))
    return dict(form=form)


def login_user(user, remember_me, email, password):
    flask_login.login_user(user, remember=remember_me)
    flask.session['token'] = user.token
    if remember_me:
        flask.session['email'] = email
        flask.session['password'] = password


@view()
def logout():
    if flask_login.current_user.is_authenticated():
        flask_login.logout_user()
    return flask.redirect(flask.url_for('auth.login'))


@view()
def register(env):
    register_form = RegisterForm(env.api)
    if register_form.validate_on_submit():
        login_user(register_form.result, False, register_form.result.email, register_form.password.data)
        return flask.redirect(flask.url_for('index'))
    return dict(form=register_form)
