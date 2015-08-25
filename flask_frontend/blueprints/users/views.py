# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask
import flask_login
import flask_gravatar
from flask_babel import gettext

from . import users_blueprint
from flask.ext.frontend.blueprints.users.helpers import only_current_user
from flask_frontend.common.const import SEX, FLASH_TYPES
from flask_frontend.blueprints.users.forms import ChangeEmailForm, ChangeBasicDataForm
from flask_frontend.common.api_helper import get_or_404, get_or_500


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
    user = get_or_404(users_blueprint.api.users.get_single, user_id)
    return flask.render_template("profile_base.html", user=user, view='users.profile_subview')


@users_blueprint.route("/<int:user_id>/profile")
def profile_subview(user_id):
    user = get_or_404(users_blueprint.api.users.get_single, user_id)
    return flask.render_template("user_profile.html", user=user)


@users_blueprint.route("/<int:user_id>/invite", methods=["POST"])
@flask_login.login_required
def invite_to_friends(user_id):
    me = flask_login.current_user
    result = users_blueprint.api.friendship_invites.create(me.token, me.id, user_id)
    if result.ok:
        flask.flash(gettext("Succesfully invited user to friends!"), FLASH_TYPES.SUCCESS)
    else:
        flask.flash(gettext("Unable to add user to friends"), FLASH_TYPES.ERROR)
    return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))


@users_blueprint.route("/<int:user_id>/accept_invitation", methods=["POST"])
@flask_login.login_required
def accept_invite_to_friends(user_id):
    me = flask_login.current_user
    user = get_or_404(users_blueprint.api.users.get_single, user_id)
    if user.relation_to_current_user.invite_received:
        result = users_blueprint.api.friendship_invites.accept(me.token, user.relation_to_current_user.id)
        if result.ok:
            flask.flash(gettext("Succesfully accepted invite to friends!"), FLASH_TYPES.SUCCESS)
            return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))

    flask.flash(gettext("Unable to accept invitation"), FLASH_TYPES.ERROR)
    return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))


@users_blueprint.route("/<int:user_id>/decline_invitation", methods=["POST"])
@flask_login.login_required
def decline_invite_to_friends(user_id):
    me = flask_login.current_user
    user = get_or_404(users_blueprint.api.users.get_single, user_id)
    relation = user.relation_to_current_user
    if relation.invite_received or relation.invite_send:
        result = users_blueprint.api.friendship_invites.delete(me.token, relation.id)
        if result.ok:
            flask.flash(gettext("Invitation declined"), FLASH_TYPES.SUCCESS)
            return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))

    flask.flash(gettext("Unable to decline invitation"), FLASH_TYPES.ERROR)
    return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))


@users_blueprint.route("/<int:user_id>/remove_friend", methods=["POST"])
@flask_login.login_required
def remove_from_friends(user_id):
    me = flask_login.current_user
    user = get_or_404(users_blueprint.api.users.get_single, user_id)
    relation = user.relation_to_current_user
    if relation.is_friend:
        result = users_blueprint.api.friendships.delete(me.token, relation.id)
        if result.ok:
            flask.flash(gettext("Friend removed"), FLASH_TYPES.SUCCESS)
            return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))

    flask.flash(gettext("Unable to remove user from friends"), FLASH_TYPES.ERROR)
    return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))


@users_blueprint.route("/<int:user_id>/friends")
@only_current_user
@flask_login.login_required
def friends_subview(user_id):
    friends = get_or_500(users_blueprint.api.users.get, friends_of_user_id=flask_login.current_user.id)
    return flask.render_template("user_friends.html", friends=friends, user=flask_login.current_user)


@users_blueprint.route("/<int:user_id>/edit")
@only_current_user
@flask_login.login_required
def edit_profile_subview(user_id):
    change_email_form = ChangeEmailForm(users_blueprint.api, flask_login.current_user)
    change_basic_form = ChangeBasicDataForm(users_blueprint.api, flask_login.current_user)
    change_basic_form.set_data(flask_login.current_user)
    return flask.render_template(
        "edit_profile.html", user=flask_login.current_user, email_form=change_email_form, basic_form=change_basic_form)


@users_blueprint.route("/<int:user_id>/edit_email", methods=["POST"])
@only_current_user
@flask_login.login_required
def change_email(user_id):
    change_email_form = ChangeEmailForm(users_blueprint.api, flask_login.current_user)
    change_basic_form = ChangeBasicDataForm(users_blueprint.api, flask_login.current_user)
    change_basic_form.set_data(flask_login.current_user)

    if change_email_form.validate_on_submit():
        flask.flash(gettext('Successfully changed email!'))

    return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))


@users_blueprint.route("/<int:user_id>/edit_basic", methods=["POST"])
@only_current_user
@flask_login.login_required
def change_basic(user_id):
    change_email_form = ChangeEmailForm(users_blueprint.api, flask_login.current_user)
    change_basic_form = ChangeBasicDataForm(users_blueprint.api, flask_login.current_user)

    if change_basic_form.validate_on_submit():
        flask.flash(gettext('Successfully changed basic data!'))

    return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))
