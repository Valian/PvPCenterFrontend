# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask_login
from flask_frontend.blueprints.users.forms import ChangeBasicDataForm, ChangeAvatarForm
from flask_frontend.common.api_helper import get_or_404, get_or_500
from flask_frontend.common.utils import CustomRoute, first_or_none


class UserRoute(CustomRoute):

    def prepare_view(self, user_id):
        token = flask_login.current_user.token if flask_login.current_user.is_authenticated() else None
        user = get_or_404(self.blueprint.api.users.get_single, user_id, token)
        return dict(user=user)


class UserFriendEditRoute(UserRoute):

    def prepare_view(self, user_id):
        params = super(UserFriendEditRoute, self).prepare_view(user_id)
        params.update(friendship_invite=self.get_friendship_invite(user_id), friendship=self.get_frienship(user_id))
        return params

    def get_friendship_invite(self, user_id):
        me = flask_login.current_user
        relations = get_or_500(self.blueprint.api.friendship_invites.get, me.token, me.id, user_id)
        relation = first_or_none(relations)
        return relation

    def get_frienship(self, user_id):
        me = flask_login.current_user
        friendships = get_or_500(self.blueprint.api.friendships.get, me.token, me.id, user_id)
        friendship = first_or_none(friendships)
        return friendship


class UserEditRoute(CustomRoute):

    def prepare_view(self, user_id):
        logged_user = flask_login.current_user
        change_basic_form = ChangeBasicDataForm(self.blueprint.api, logged_user)
        change_basic_form.set_data(flask_login.current_user)
        avatar_form = ChangeAvatarForm(logged_user.id, logged_user.token, self.blueprint.api)
        return dict(user=logged_user, basic_form=change_basic_form, avatar_form=avatar_form)
