# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import datetime

from flask import url_for
import mock

from api.core import ApiResult
from api.mock import create_mock_for
from api.models import User, ModelList, FriendshipInvite, TeamMembership, Friendship
from api.constants import RELATION_TO_CURRENT_USER
from flask_frontend.common.app_test_case import AppTestCase, logged_in, mock_api


class UsersTests(AppTestCase):

    @mock_api(User, 'get_single')
    def test_user_profile(self, get_single):
        self.client.get(url_for('users.user_view', user_id=1))
        self.assertTrue(get_single.called)

    @mock_api(User, 'get_single')
    def test_my_profile_edit_fails_without_login(self, get_single):
        response = self.client.get(url_for('users.edit_profile_view', user_id=1), expect_errors=True)
        self.assertEqual(response.status_code, 403)

    @logged_in()
    def test_profile_edit_pass_when_logged(self, user):
        response = self.client.get(url_for('users.edit_profile_view', user_id=user.id))
        self.assertEqual(response.status_code, 200)

    @mock_api(Friendship, 'get')
    @logged_in()
    def test_my_friends_calls_api(self, get, user):
        response = self.client.get(url_for('users.friends_view', user_id=user.id))
        self.assertEqual(get.call_count, 1)
        call_kwargs = get.call_args[1]
        self.assertIn('user_id', call_kwargs)
        self.assertEqual(call_kwargs['user_id'], user.id)
        self.assertIn('friendships', response.context)
        self.assertIsInstance(response.context['friendships'], list)

    @mock_api(FriendshipInvite, 'create')
    @logged_in(id=5)
    def test_invite_friend_calls_api(self, create, user):
        self.client.post(url_for('users.invite_to_friends', user_id=8))
        self.assertTrue(create.called)
        self.assertEqual(create.call_args, mock.call(token=user.token, from_user_id=user.id, to_user_id=8))

    @mock_api(FriendshipInvite, 'get', list_count=1)
    @mock_api(FriendshipInvite, 'accept')
    @logged_in(relation_to_current_user=RELATION_TO_CURRENT_USER.RECEIVED_INVITE)
    def test_accept_friend_invite_calls_api(self, get, accept, user):
        self.client.post(url_for('users.accept_invite', user_id=5))
        self.assertTrue(accept.called)
        self.assertEqual(accept.call_args, mock.call(
            token=user.token, friendship_invite_id=get.return_value.data[0].id))

    @mock_api(FriendshipInvite, 'get', list_count=1)
    @mock_api(FriendshipInvite, 'delete')
    @logged_in(relation_to_current_user=RELATION_TO_CURRENT_USER.RECEIVED_INVITE)
    def test_decline_friend_invite_calls_api(self, get, delete, user):
        self.client.post(url_for('users.decline_invite', user_id=5))
        self.assertTrue(delete.called)
        self.assertEqual(delete.call_args, mock.call(
            token=user.token, friendship_invite_id=get.return_value.data[0].id))

    @mock_api(Friendship, 'delete')
    @mock_api(Friendship, 'get', list_count=1, friend__id=5)
    @logged_in(relation_to_current_user=RELATION_TO_CURRENT_USER.FRIEND)
    def test_remove_friend_calls_api(self, delete, get, user):
        self.client.post(url_for('users.remove_from_friends', user_id=5))
        self.assertTrue(delete.called)
        self.assertEqual(delete.call_args, mock.call(
            token=user.token, friendship_id=get.return_value.data[0].id))

    @mock_api(FriendshipInvite, 'delete')
    @mock_api(FriendshipInvite, 'get', list_count=1, from_user__id=5)
    @logged_in(relation_to_current_user=RELATION_TO_CURRENT_USER.RECEIVED_INVITE)
    def test_remove_sent_friendship_invitation_calls_api(self, delete, get, user):
        self.client.post(url_for('users.decline_invite', user_id=5))
        self.assertTrue(delete.called)
        self.assertEqual(delete.call_args, mock.call(
            token=user.token, friendship_invite_id=get.return_value.data[0].id))

    @mock_api(TeamMembership, 'get')
    def test_show_user_teams(self, get):
        response = self.client.get(url_for('users.teams_view', user_id=5))
        self.assertIsInstance(response.context['teams'], list)

    @mock_api(User, 'update')
    @logged_in(id=5)
    def test_basic_info_edit(self, update, user):
        nationality = 'US'
        birthdate = datetime.date(1992, 12, 23)
        about_me = 'Me like me'
        sex = 'F'
        data = {'nationality': nationality, 'birthdate': birthdate, 'description': about_me, 'sex': sex}
        response = self.client.post(url_for('users.change_basic', user_id=user.id), params=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(update.call_count, 1)
        self.assertEqual(update.call_args, mock.call(
            user_id=user.id, token=user.token, nationality=nationality, sex=sex, description=about_me,
            birthdate=birthdate))

