# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask
import flask_login
import flask_gravatar
from flask_babel import gettext

from . import users_blueprint
from flask_frontend.common.const import SEX
from flask_frontend.blueprints.users.forms import ChangeEmailForm, ChangeBasicDataForm
from flask_frontend.common.api_helper import get_or_404, get_or_none


def sex_to_text(value):
    if value == SEX.MALE:
        return gettext('Male')
    if value == SEX.FEMALE:
        return gettext('Female')
    return 'Not specified'


@users_blueprint.record_once
def init(state):
    app = state.app
    gravatar = flask_gravatar.Gravatar()
    gravatar.init_app(app)
    app.jinja_env.filters['sex'] = sex_to_text


@users_blueprint.route("/<int:user_id>")
def profile_view(user_id):
    user = get_or_404(users_blueprint.api.user.get, user_id)
    return flask.render_template("user_profile.html", user=user)


@users_blueprint.route("/<int:user_id>/friends")
@flask_login.login_required
def my_friends_view(user_id):
    if user_id != flask_login.current_user.id:
        flask.abort(403)
    friends = get_or_none(users_blueprint.api.users.get, friends_of_user_id=flask_login.current_user.id) or []
    return flask.render_template("user_friends.html", friends=friends, user=flask_login.current_user)


@users_blueprint.route("/<int:user_id>/edit")
@flask_login.login_required
def edit_profile_view(user_id):
    if user_id != flask_login.current_user.id:
        flask.abort(403)

    change_email_form = ChangeEmailForm(users_blueprint.api, flask_login.current_user)
    change_basic_form = ChangeBasicDataForm(users_blueprint.api, flask_login.current_user)
    change_basic_form.set_data(flask_login.current_user)
    return flask.render_template(
        "edit_profile.html", user=flask_login.current_user, email_form=change_email_form, basic_form=change_basic_form)


@users_blueprint.route("/<int:user_id>/edit_email", methods=["POST"])
@flask_login.login_required
def change_email(user_id):
    if user_id != flask_login.current_user.id:
        flask.abort(403)

    change_email_form = ChangeEmailForm(users_blueprint.api, flask_login.current_user)
    change_basic_form = ChangeBasicDataForm(users_blueprint.api, flask_login.current_user)
    change_basic_form.set_data(flask_login.current_user)

    if change_email_form.validate_on_submit():
        flask.flash(gettext('Successfully changed email!'))

    return flask.render_template(
        "edit_profile.html", user=flask_login.current_user, email_form=change_email_form, basic_form=change_basic_form)


@users_blueprint.route("/<int:user_id>/edit_basic", methods=["POST"])
@flask_login.login_required
def change_basic(user_id):
    if user_id != flask_login.current_user.id:
        flask.abort(403)

    change_email_form = ChangeEmailForm(users_blueprint.api, flask_login.current_user)
    change_basic_form = ChangeBasicDataForm(users_blueprint.api, flask_login.current_user)

    if change_basic_form.validate_on_submit():
        flask.flash(gettext('Successfully changed basic data!'))

    return flask.render_template(
        "edit_profile.html", user=flask_login.current_user, email_form=change_email_form, basic_form=change_basic_form)
