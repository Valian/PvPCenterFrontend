# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask import url_for
import mock

from api.api import ApiResult
from api.mock import create_mock_for
from api.models import User
from flask_frontend.common.app_test_case import AppTestCase


@mock.patch('flask_frontend.blueprints.users.views.users_blueprint.api')
class UsersTests(AppTestCase):

    def test_user_profile(self, api_mock):
        return_user = create_mock_for(User)
        api_mock.user.get.return_value = ApiResult(data=return_user)
        self.client.get(url_for('users.profile_view', user_id=1))
        self.assertTrue(api_mock.user.get.called)

    def test_my_profile_error_without_login(self, api_mock):
        self.login_user(api_mock)
        response = self.client.get(url_for('users.my_profile_view'), follow_redirects=False)
        self.assertEqual(response.status_code, 200)

    def test_my_profile_pass_when_logged(self, api_mock):
        return_user = create_mock_for(User)
        api_mock.user.get.return_value = ApiResult(data=return_user)
        response = self.client.get(url_for('users.my_profile_view'), follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_my_profile_edit_fails_without_login(self, api_mock):
        return_user = create_mock_for(User)
        api_mock.user.get.return_value = ApiResult(data=return_user)
        response = self.client.get(url_for('users.edit_profile_view'), follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_my_profile_edit_pass_when_logged(self, api_mock):
        self.login_user(api_mock)
        response = self.client.get(url_for('users.edit_profile_view'))
        self.assertEqual(response.status_code, 200)

    @mock.patch('flask_frontend.blueprints.auth.views.auth_blueprint.api')
    def test_profile_edit(self, auth_api_mock, api_mock):
        _, user = self.login_user(auth_api_mock)
        api_mock.user.patch.return_value = ApiResult(data=user)
        nick = "testtest"
        email = "test@test.com"
        data = {"nickname": nick, "email": email}
        response = self.client.post(url_for('users.edit_profile_view'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(api_mock.user.patch.call_count, 1)
        self.assertEqual(api_mock.user.patch.call_args, mock.call(user.id, user.token, nick, email))

