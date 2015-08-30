# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import datetime

from flask import url_for
import mock
from nose_parameterized import parameterized

from api.api import ApiResult
from api.mock import create_mock_for
from api.models import User, ModelList, FriendshipInvite, RELATION_TO_CURRENT_USER, TeamMembership
from flask_frontend.common.app_test_case import AppTestCase, logged_in


@mock.patch('flask_frontend.blueprints.users.views.users_blueprint.api')
class UsersTests(AppTestCase):

    def test_user_profile(self, api_mock):
        return_user = create_mock_for(User)
        api_mock.users.get_single.return_value = ApiResult(data=return_user)
        self.client.get(url_for('users.profile_view', user_id=1))
        self.assertTrue(api_mock.users.get_single.called)

    def test_my_profile_edit_fails_without_login(self, api_mock):
        return_user = create_mock_for(User)
        api_mock.users.get_single.return_value = ApiResult(data=return_user)
        response = self.client.get(url_for('users.edit_profile_view', user_id=return_user.id), expect_errors=True)
        self.assertEqual(response.status_code, 403)

    @logged_in
    def test_profile_edit_pass_when_logged(self, user, api_mock):
        response = self.client.get(url_for('users.edit_profile_view', user_id=user.id))
        self.assertEqual(response.status_code, 200)

    @logged_in
    def test_my_friends_calls_api(self, user, api_mock):
        data = create_mock_for(ModelList.For(User), 3)
        api_mock.users.get.return_value = ApiResult(data=data)
        response = self.client.get(url_for('users.friends_view', user_id=user.id))
        self.assertEqual(api_mock.users.get.call_count, 1)
        call_kwargs = api_mock.users.get.call_args[1]
        self.assertIn('friends_of_user_id', call_kwargs)
        self.assertEqual(call_kwargs['friends_of_user_id'], user.id)
        self.assertIn('friends', response.context)
        self.assertIsInstance(response.context['friends'], list)

    @logged_in
    def test_invite_friend_calls_api(self, user, api_mock):
        self.client.post(url_for('users.invite_to_friends', user_id=8))
        self.assertTrue(api_mock.friendship_invites.create.called)
        self.assertEqual(api_mock.friendship_invites.create.call_args, mock.call(user.token, user.id, 8))

    @logged_in
    def test_accept_friend_invite_calls_api(self, user, api_mock):
        return_user = create_mock_for(User, relation_to_current_user__type=RELATION_TO_CURRENT_USER.RECEIVED_INVITE)
        api_mock.users.get_single.return_value = ApiResult(data=return_user)
        self.client.post(url_for('users.accept_invite_to_friends', user_id=5))
        self.assertTrue(api_mock.friendship_invites.accept.called)
        self.assertEqual(api_mock.friendship_invites.accept.call_args, mock.call(
            user.token, return_user.relation_to_current_user.id))

    @logged_in
    def test_decline_friend_invite_calls_api(self, user, api_mock):
        return_user = create_mock_for(User, relation_to_current_user__type=RELATION_TO_CURRENT_USER.RECEIVED_INVITE)
        api_mock.users.get_single.return_value = ApiResult(data=return_user)
        self.client.post(url_for('users.decline_invite_to_friends', user_id=5))
        self.assertTrue(api_mock.friendship_invites.delete.called)
        self.assertEqual(api_mock.friendship_invites.delete.call_args, mock.call(
            user.token, return_user.relation_to_current_user.id))

    @logged_in
    def test_remove_friend_calls_api(self, user, api_mock):
        return_user = create_mock_for(User, relation_to_current_user__type=RELATION_TO_CURRENT_USER.FRIEND)
        api_mock.users.get_single.return_value = ApiResult(data=return_user)
        self.client.post(url_for('users.remove_from_friends', user_id=5))
        self.assertTrue(api_mock.friendships.delete.called)
        self.assertEqual(api_mock.friendships.delete.call_args, mock.call(
            user.token, return_user.relation_to_current_user.id))

    @logged_in
    def test_remove_sent_friendship_invitation_calls_api(self, user, api_mock):
        return_user = create_mock_for(User, relation_to_current_user__type=RELATION_TO_CURRENT_USER.SEND_INVITE)
        api_mock.users.get_single.return_value = ApiResult(data=return_user)
        self.client.post(url_for('users.decline_invite_to_friends', user_id=5))
        self.assertTrue(api_mock.friendship_invites.delete.called)
        self.assertEqual(api_mock.friendship_invites.delete.call_args, mock.call(
            user.token, return_user.relation_to_current_user.id))

    def test_show_user_teams(self, api_mock):
        return_user = create_mock_for(User)
        returned_teams = create_mock_for(ModelList.For(TeamMembership))
        api_mock.users.get_single.return_value = ApiResult(data=return_user)
        api_mock.team_memberships.get.return_value = ApiResult(data=returned_teams)
        response = self.client.get(url_for('users.teams_view', user_id=5))
        self.assertIsInstance(response.context['teams'], list)

class UsersWithAuthTests(AppTestCase):

    @parameterized.expand([
        ({'email': "dupa@dupa.com", 'repeat': "other"}, False),
        ({'email': "dupa", 'repeat': "dupa"}, False),
        ({'email': "dupa@dupa.com", 'repeat': "dupa@dupa.com"}, True)
    ])
    @mock.patch('flask_frontend.blueprints.users.views.users_blueprint.api')
    @mock.patch('flask_frontend.blueprints.auth.views.auth_blueprint.api')
    def test_email_edit(self, data, should_call_api, auth_api_mock, api_mock):
        _, user = self.login_user(auth_api_mock)
        api_mock.users.patch.return_value = ApiResult(data=user)
        response = self.client.post(url_for('users.change_email', user_id=user.id), params=data)
        self.assertEqual(response.status_code, 302)
        if should_call_api:
            self.assertEqual(api_mock.users.patch.call_count, 1)
            self.assertEqual(api_mock.users.patch.call_args, mock.call(user.id, user.token, email=data['email']))
        else:
            self.assertFalse(api_mock.users.patch.called)

    @mock.patch('flask_frontend.blueprints.users.views.users_blueprint.api')
    @mock.patch('flask_frontend.blueprints.auth.views.auth_blueprint.api')
    def test_basic_info_edit(self, auth_api_mock, api_mock):
        _, user = self.login_user(auth_api_mock)
        api_mock.users.patch.return_value = ApiResult(data=user)
        nationality = 'en'
        birthdate = datetime.date(1992, 12, 23)
        about_me = 'Me like me'
        sex = 1
        data = {'nationality': nationality, 'birthdate': birthdate, 'description': about_me, 'sex': sex}
        response = self.client.post(url_for('users.change_basic', user_id=user.id), params=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(api_mock.users.patch.call_count, 1)
        self.assertEqual(api_mock.users.patch.call_args, mock.call(
            user.id, user.token, nationality=nationality, sex=sex, description=about_me, birthdate=birthdate))

