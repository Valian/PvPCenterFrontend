# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask
import flask_login
from flask_babel import gettext

from api.models import User, Friendship, Team
from flask_frontend.blueprints.users.forms import ChangeBasicDataForm, ChangeAvatarForm
from flask_frontend.common.view_helpers.response_processors import PjaxView, pjax_view, template_view
from flask_frontend.common.view_helpers.contexts import ApiResourceGet, ApiResourceIndex, model_view
from flask_frontend.common.view_helpers.routes import UrlRoute, UrlRoutes
from flask_frontend.blueprints.users.helpers import only_current_user
from flask_frontend.common.flash import Flash
from flask_frontend.common.utils import first_or_none, restrict
from flask_frontend.common.api_helper import get_or_500, get_or_404


def create_routes():
    friends_context_creators = [ApiResourceGet(User), ApiResourceIndex(Friendship, allowed_params=['user_id'])]
    teams_context_creators = [ApiResourceGet(User), ApiResourceIndex(Team, allowed_params=['user_id'])]
    friends_view = PjaxView("user_friends.html", friends_context_creators, decorators=[restrict(only_current_user)])
    teams_view = PjaxView('user_teams.html', teams_context_creators)
    users_view = PjaxView('users_list.html', ApiResourceIndex(User, allowed_params=['nickname']))
    user_view = PjaxView('user_profile.html', ApiResourceGet(User))
    return UrlRoutes([
        UrlRoute('/', users_view, endpoint="users_view"),
        UrlRoute('/<int:user_id>/', user_view, endpoint="user_view"),
        UrlRoute('/<int:user_id>/teams', teams_view, endpoint='teams_view'),
        UrlRoute('/<int:user_id>/invite', invite_to_friends, methods=['POST']),
        UrlRoute('/<int:user_id>/accept_invitation', accept_invite, methods=["POST"]),
        UrlRoute('/<int:user_id>/decline_invitation', decline_invite, methods=["POST"]),
        UrlRoute('/<int:user_id>/remove_from_friends', remove_from_friends, methods=["POST"]),
        UrlRoute('/<int:user_id>/friends', friends_view, endpoint='friends_view'),
        UrlRoute('/<int:user_id>/edit', edit_profile_view),
        UrlRoute('/<int:user_id>/change_basic', change_basic, methods=['POST']),
        UrlRoute('/<int:user_id>/upload_avatar', upload_avatar, methods=['POST'])
    ])


@flask_login.login_required
def user_edit_friendship_context(self, env, **kwargs):
    me = flask_login.current_user
    user_id = kwargs['user_id']
    return dict(
        user=get_or_404(self.blueprint.api.users.get_single, user_id=user_id, token=me.token),
        friendship_invite=first_or_none(get_or_500(env.api.friendship_invites.get, token=me.token, from_user_id=me.id, to_user_id=user_id)),
        friendship=first_or_none(get_or_500(env.api.friendships.get, token=me.token, user_id=me.id, to_user_id=user_id)))


@model_view(User)
def invite_to_friends(env, user):
    me = flask_login.current_user
    result = get_or_500(env.api.friendship_invites.create, me.token, me.id, user.id)
    if result:
        Flash.success(gettext("Succesfully invited user to friends!"))
    else:
        Flash.error(gettext("Unable to add user to friends"))
    # TODO - return to referrer
    return flask.redirect(flask.url_for('users.user_view', user_id=user.id))


@template_view('user_profile.html', user_edit_friendship_context)
def accept_invite(env, friendship_invite):
    if friendship_invite:
        result = env.api.friendship_invites.accept(flask_login.current_user.token, friendship_invite.id)
        if result.ok:
            Flash.success(gettext("Succesfully accepted invite to friends!"))
            return
    Flash.error(gettext("Unable to accept invitation"))


@template_view('user_profile.html', user_edit_friendship_context)
def decline_invite(env, friendship_invite):
    if friendship_invite:
        result = env.api.friendship_invites.delete(flask_login.current_user.token, friendship_invite.id)
        if result.ok:
            Flash.success(gettext("Invitation declined"))
            return
    Flash.success(gettext("Unable to decline invitation"))


@template_view('user_profile.html', user_edit_friendship_context)
def remove_from_friends(env, friendship):
    if friendship:
        result = env.api.friendships.delete(flask_login.current_user.token, friendship.id)
        if result.ok:
            Flash.success(gettext("Friend removed"))
            return
    Flash.error(gettext("Unable to remove user from friends"))


@restrict(only_current_user)
def user_edit_context(env, **kwargs):
    logged_user = flask_login.current_user
    change_basic_form = ChangeBasicDataForm(env.api, logged_user)
    avatar_form = ChangeAvatarForm(logged_user.id, logged_user.token, env.api)
    return dict(user=logged_user, basic_form=change_basic_form, avatar_form=avatar_form)


@pjax_view("edit_profile.html", user_edit_context)
def edit_profile_view(basic_form):
    basic_form.set_data(flask_login.current_user)


@pjax_view("edit_profile.html", user_edit_context)
def upload_avatar(avatar_form):
    if avatar_form.validate_on_submit():
        Flash.success("Succesfully updated image!")


@pjax_view("edit_profile.html", user_edit_context)
def change_basic(basic_form):
    if basic_form.validate_on_submit():
        Flash.success(gettext('Successfully changed basic data!'))
