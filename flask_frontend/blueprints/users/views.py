# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask
import flask_login
import flask_gravatar
from flask_babel import gettext

from . import users_blueprint
from flask_frontend.blueprints.users.helpers import only_current_user
from flask_frontend.blueprints.users.routes import UserRoute, UserEditRoute, UserFriendEditRoute
from flask_frontend.common.flash import Flash
from flask_frontend.common.pagination import Pagination
from flask_frontend.common.utils import render_pjax
from flask_frontend.common.const import SEX
from flask_frontend.common.api_helper import get_or_500


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


user_route = UserRoute(users_blueprint, "/<int:user_id>")
edit_user_route = UserEditRoute(users_blueprint, "/<int:user_id>")
edit_friendship_route = UserFriendEditRoute(users_blueprint, "/<int:user_id>")


@users_blueprint.route("/")
def users_view():
    nickname = flask.request.args.get('nickname', '')
    users = get_or_500(users_blueprint.api.users.get, nickname=nickname)
    pagination = Pagination.create_from_model_list(users)
    return render_pjax("users_list.html", "users_list_result.html", pagination=pagination, users=users)


@user_route('')
def profile_view(user):
    return render_pjax("profile_base.html", "user_profile.html", user=user)


@user_route("/teams")
def teams_view(user):
    teams_memberships = get_or_500(users_blueprint.api.team_memberships.get, user_id=user.id)
    teams = map(lambda tm: tm.team, teams_memberships)
    return render_pjax("profile_base.html", "user_teams.html", user=user, teams=teams)


@user_route("/invite", methods=["POST"])
@flask_login.login_required
def invite_to_friends(user):
    me = flask_login.current_user
    result = get_or_500(users_blueprint.api.friendship_invites.create, me.token, me.id, user.id)
    if result:
        Flash.success(gettext("Succesfully invited user to friends!"))
    else:
        Flash.error(gettext("Unable to add user to friends"))
    # TODO - return to referrer
    return flask.redirect(flask.url_for('users.profile_view', user_id=user.id))


@edit_friendship_route("/accept_invitation", methods=["POST"])
@flask_login.login_required
def accept_invite_to_friends(user, friendship, friendship_invite):
    if friendship_invite:
        result = users_blueprint.api.friendship_invites.accept(flask_login.current_user.token, friendship_invite.id)
        if result.ok:
            Flash.success(gettext("Succesfully accepted invite to friends!"))
            return render_pjax("profile_base.html", "user_profile.html", user=user)

    Flash.error(gettext("Unable to accept invitation"))
    return render_pjax("profile_base.html", "user_profile.html", user=user)


@edit_friendship_route("/decline_invitation", methods=["POST"])
@flask_login.login_required
def decline_invite_to_friends(user, friendship, friendship_invite):
    if friendship_invite:
        result = users_blueprint.api.friendship_invites.delete(flask_login.current_user.token, friendship_invite.id)
        if result.ok:
            Flash.success(gettext("Invitation declined"))
            return render_pjax("profile_base.html", "user_profile.html", user=user)

    Flash.success(gettext("Unable to decline invitation"))
    return render_pjax("profile_base.html", "user_profile.html", user=user)


@edit_friendship_route("/remove_friend", methods=["POST"])
@flask_login.login_required
def remove_from_friends(user, friendship, friendship_invite):
    if friendship:
        result = users_blueprint.api.friendships.delete(flask_login.current_user.token, friendship.id)
        if result.ok:
            Flash.success(gettext("Friend removed"))
            return render_pjax("profile_base.html", "user_profile.html", user=user)

    Flash.error(gettext("Unable to remove user from friends"))
    return render_pjax("profile_base.html", "user_profile.html", user=user)


@user_route("/friends")
@only_current_user
def friends_view(user):
    current_user = flask_login.current_user
    friendships = get_or_500(users_blueprint.api.friendships.get, token=current_user.token, user_id=user.id)
    pagination = Pagination.create_from_model_list(friendships)
    return render_pjax(
        "profile_base.html", "user_friends.html", friendships=friendships, user=user, pagination=pagination)


@edit_user_route("/edit")
@only_current_user
def edit_profile_view(user, avatar_form, basic_form):
    return render_pjax(
        "profile_base.html", "edit_profile.html", user=user, basic_form=basic_form,
        avatar_form=avatar_form)


@edit_user_route("/upload_avatar", methods=["POST"])
@only_current_user
def upload_avatar(user, avatar_form, basic_form):
    if avatar_form.validate_on_submit():
        Flash.success("Succesfully updated image!")
    return render_pjax(
        "profile_base.html", "edit_profile.html", user=user, basic_form=basic_form, avatar_form=avatar_form)


@edit_user_route("/edit_basic", methods=["POST"])
@only_current_user
def change_basic(user, avatar_form, basic_form):
    if basic_form.validate_on_submit():
        Flash.success(gettext('Successfully changed basic data!'))

    return render_pjax(
        "profile_base.html", "edit_profile.html", user=user, avatar_form=avatar_form, basic_form=basic_form)
