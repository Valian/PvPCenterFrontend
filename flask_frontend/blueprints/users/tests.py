# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import datetime

from flask import url_for
import mock
from nose_parameterized import parameterized

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
        response = self.client.get(url_for('users.my_profile_view'))
        self.assertEqual(response.status_code, 200)

    def test_my_profile_pass_when_logged(self, api_mock):
        return_user = create_mock_for(User)
        api_mock.user.get.return_value = ApiResult(data=return_user)
        response = self.client.get(url_for('users.my_profile_view'))
        self.assertEqual(response.status_code, 302)

    def test_my_profile_edit_fails_without_login(self, api_mock):
        return_user = create_mock_for(User)
        api_mock.user.get.return_value = ApiResult(data=return_user)
        response = self.client.get(url_for('users.edit_profile_view'))
        self.assertEqual(response.status_code, 302)

    def test_my_profile_edit_pass_when_logged(self, api_mock):
        self.login_user(api_mock)
        response = self.client.get(url_for('users.edit_profile_view'))
        self.assertEqual(response.status_code, 200)


class EditUserTests(AppTestCase):

    @parameterized.expand([
        ({'email': "dupa@dupa.com", 'repeat': "other"}, False),
        ({'email': "dupa", 'repeat': "dupa"}, False),
        ({'email': "dupa@dupa.com", 'repeat': "dupa@dupa.com"}, True)
    ])
    @mock.patch('flask_frontend.blueprints.users.views.users_blueprint.api')
    @mock.patch('flask_frontend.blueprints.auth.views.auth_blueprint.api')
    def test_email_edit(self, data, should_call_api, auth_api_mock, api_mock):
        _, user = self.login_user(auth_api_mock)
        api_mock.user.patch.return_value = ApiResult(data=user)
        response = self.client.post(url_for('users.change_email'), params=data)
        self.assertEqual(response.status_code, 200)
        if should_call_api:
            self.assertEqual(api_mock.user.patch.call_count, 1)
            self.assertEqual(api_mock.user.patch.call_args, mock.call(user.id, user.token, email=data['email']))
        else:
            self.assertFalse(api_mock.user.patch.called)

    @mock.patch('flask_frontend.blueprints.users.views.users_blueprint.api')
    @mock.patch('flask_frontend.blueprints.auth.views.auth_blueprint.api')
    def test_basic_info_edit(self, auth_api_mock, api_mock):
        _, user = self.login_user(auth_api_mock)
        api_mock.user.patch.return_value = ApiResult(data=user)
        nationality = 'en'
        birthdate = datetime.date(1992, 12, 23)
        about_me = 'Me like me'
        sex = 1
        data = {'nationality': nationality, 'birthdate': birthdate, 'description': about_me, 'sex': sex}
        response = self.client.post(url_for('users.change_basic'), params=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(api_mock.user.patch.call_count, 1)
        self.assertEqual(api_mock.user.patch.call_args, mock.call(
            user.id, user.token, nationality=nationality, sex=sex, description=about_me, birthdate=birthdate))

