# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask
import flask_login
import flask_gravatar

from flask_babel import gettext

from . import users_blueprint
from flask_frontend.blueprints.users.forms import EditProfileForm
from flask_frontend.common.api_helper import get_or_404


@users_blueprint.record_once
def init(state):
    app = state.app
    gravatar = flask_gravatar.Gravatar()
    gravatar.init_app(app)


@users_blueprint.route("/<int:user_id>")
def profile_view(user_id):
    user = get_or_404(users_blueprint.api.user.get, user_id)
    return flask.render_template("user_profile.html", user=user)


@users_blueprint.route("/my_profile")
@flask_login.login_required
def my_profile_view():
    return flask.render_template("my_profile.html")


@users_blueprint.route("/my_profile/edit", methods=['POST', 'GET'])
@flask_login.login_required
def edit_profile_view():
    edit_profile_form = EditProfileForm(
        users_blueprint.api, flask_login.current_user.id, flask_login.current_user.token)
    if flask.request.method == "GET":
        edit_profile_form.nickname.data = flask_login.current_user.name
        edit_profile_form.email.data = flask_login.current_user.email

    if edit_profile_form.validate_on_submit():
        flask.flash(gettext('Profile data successfully updated'))

    return flask.render_template("edit_profile.html", form=edit_profile_form)
