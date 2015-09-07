# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask
import flask_login
import flask_gravatar
from flask_babel import gettext

from . import users_blueprint
from flask.ext.frontend.blueprints.users.helpers import only_current_user
from flask.ext.frontend.common.flash import Flash
from flask.ext.frontend.common.pagination import get_pagination_params, Pagination
from flask.ext.frontend.common.utils import render_pjax, first_or_none
from flask_frontend.common.const import SEX
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


@users_blueprint.route("/")
def users_view():
    nickname = flask.request.args.get('nickname', '')
    users = get_or_500(users_blueprint.api.users.get, nickname=nickname)
    pagination = Pagination.create_from_model_list(users)
    return render_pjax("users_list.html", "users_list_result.html", pagination=pagination, users=users)


@users_blueprint.route("/<int:user_id>")
@users_blueprint.route("/<int:user_id>/profile")
def profile_view(user_id):
    token = flask_login.current_user.token if flask_login.current_user.is_authenticated() else None
    user = get_or_404(users_blueprint.api.users.get_single, user_id, token=token)
    return render_pjax("profile_base.html", "user_profile.html", user=user)


@users_blueprint.route("/<int:user_id>/teams")
def teams_view(user_id):
    user = get_or_404(users_blueprint.api.users.get_single, user_id)
    teams_memberships = get_or_500(users_blueprint.api.team_memberships.get, user_id=user_id)
    teams = map(lambda tm: tm.team, teams_memberships)
    return render_pjax("profile_base.html", "user_teams.html", user=user, teams=teams)


@users_blueprint.route("/<int:user_id>/invite", methods=["POST"])
@flask_login.login_required
def invite_to_friends(user_id):
    me = flask_login.current_user
    result = users_blueprint.api.friendship_invites.create(me.token, me.id, user_id)
    if result.ok:
        Flash.success(gettext("Succesfully invited user to friends!"))
    else:
        Flash.error(gettext("Unable to add user to friends"))
    return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))


@users_blueprint.route("/<int:user_id>/accept_invitation", methods=["POST"])
@flask_login.login_required
def accept_invite_to_friends(user_id):
    relation = get_friendship_invite(user_id)
    if relation:
        result = users_blueprint.api.friendship_invites.accept(flask_login.current_user.token, relation.id)
        if result.ok:
            Flash.success(gettext("Succesfully accepted invite to friends!"))
            return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))

    Flash.error(gettext("Unable to accept invitation"))
    return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))


def get_friendship_invite(user_id):
    me = flask_login.current_user
    relations = get_or_500(users_blueprint.api.friendship_invites.get, me.token, me.id, user_id)
    relation = first_or_none(relations)
    return relation


def get_frienship(user_id):
    me = flask_login.current_user
    friendships = get_or_500(users_blueprint.api.friendships.get, me.token, me.id, user_id)
    friendship = first_or_none(friendships)
    return friendship


@users_blueprint.route("/<int:user_id>/decline_invitation", methods=["POST"])
@flask_login.login_required
def decline_invite_to_friends(user_id):
    relation = get_friendship_invite(user_id)
    if relation:
        result = users_blueprint.api.friendship_invites.delete(flask_login.current_user.token, relation.id)
        if result.ok:
            Flash.success(gettext("Invitation declined"))
            return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))

    Flash.success(gettext("Unable to decline invitation"))
    return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))


@users_blueprint.route("/<int:user_id>/remove_friend", methods=["POST"])
@flask_login.login_required
def remove_from_friends(user_id):
    friendship = get_frienship(user_id)
    if friendship:
        result = users_blueprint.api.friendships.delete(flask_login.current_user.token, friendship.id)
        if result.ok:
            Flash.success(gettext("Friend removed"))
            return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))

    Flash.error(gettext("Unable to remove user from friends"))
    return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))


@users_blueprint.route("/<int:user_id>/friends")
@only_current_user
@flask_login.login_required
def friends_view(user_id):
    user = flask_login.current_user
    friendships = get_or_500(users_blueprint.api.friendships.get, token=user.token, user_id=user_id)
    pagination = Pagination.create_from_model_list(friendships)
    return render_pjax(
        "profile_base.html", "user_friends.html", friendships=friendships, user=user, pagination=pagination)


@users_blueprint.route("/<int:user_id>/edit")
@only_current_user
@flask_login.login_required
def edit_profile_view(user_id):
    change_email_form = ChangeEmailForm(users_blueprint.api, flask_login.current_user)
    change_basic_form = ChangeBasicDataForm(users_blueprint.api, flask_login.current_user)
    change_basic_form.set_data(flask_login.current_user)
    return render_pjax(
        "profile_base.html", "edit_profile.html", user=flask_login.current_user, email_form=change_email_form,
        basic_form=change_basic_form)


@users_blueprint.route("/<int:user_id>/edit_email", methods=["POST"])
@only_current_user
@flask_login.login_required
def change_email(user_id):
    change_email_form = ChangeEmailForm(users_blueprint.api, flask_login.current_user)
    change_basic_form = ChangeBasicDataForm(users_blueprint.api, flask_login.current_user)
    change_basic_form.set_data(flask_login.current_user)

    if change_email_form.validate_on_submit():
        Flash.success(gettext('Successfully changed email!'))

    return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))


@users_blueprint.route("/<int:user_id>/edit_basic", methods=["POST"])
@only_current_user
@flask_login.login_required
def change_basic(user_id):
    change_email_form = ChangeEmailForm(users_blueprint.api, flask_login.current_user)
    change_basic_form = ChangeBasicDataForm(users_blueprint.api, flask_login.current_user)

    if change_basic_form.validate_on_submit():
        Flash.success(gettext('Successfully changed basic data!'))

    return flask.redirect(flask.url_for('users.profile_view', user_id=user_id))
