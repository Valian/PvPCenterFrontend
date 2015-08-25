# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import mock
from flask import url_for
from nose_parameterized import parameterized

from api.api import ApiResult
from api.mock import create_mock_for
from flask_frontend.common.app_test_case import AppTestCase
from .user import User


class AuthTests(AppTestCase):

    @mock.patch('flask_frontend.blueprints.auth.views.auth_blueprint.api')
    def test_login(self, api_mock):
        response, user = self.login_user(api_mock)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(api_mock.users.login.called)
        self.assertIn('Logout', response.body)
        logged_user = response.context['current_user']
        self.assertEqual(user, logged_user)
        self.assertTrue(logged_user.is_authenticated())

    @mock.patch('flask_frontend.blueprints.auth.views.flask_login')
    @mock.patch('flask_frontend.blueprints.auth.views.auth_blueprint.api')
    def test_login_remember_me(self, api_mock, flask_login_mock):
        response, user = self.login_user(api_mock, remember=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(api_mock.users.login.called)
        self.assertTrue(flask_login_mock.login_user.called)
        self.assertEqual(mock.call(user, remember=True), flask_login_mock.login_user.call_args)

    @parameterized.expand([
        ({'email': "dupadupa.com", 'password': "password"}, 'Invalid'),
        ({'email': "dupa@dupa", 'password': "password"}, 'Invalid'),
        ({'email': "dupadupa", 'password': "password"}, 'Invalid'),
        ({'email': "", 'password': "password"}, 'Invalid'),
        ({'email': "dupa@dupa.com", 'password': ""}, 'Min'),
        ({'email': "dupa@dupa.com", 'password': "sd"}, 'Min'),
    ])
    @mock.patch('flask_frontend.blueprints.auth.views.auth_blueprint.api')
    def test_invalid_email(self, data, error_message, api_mock):
        response, user = self.login_user(api_mock, data=data)
        self.assertFalse(api_mock.users.login.called)
        self.assertNotIn('Logout', response.body)
        self.assertIn(error_message, response.body)

    @mock.patch('flask_frontend.blueprints.auth.views.auth_blueprint.api')
    def test_logout(self, api_mock):
        response = self.client.get(url_for('index'))
        self.assertFalse(response.context['current_user'].is_authenticated())
        self.assertEqual(response.status_code, 200)
        response, user = self.login_user(api_mock)
        self.assertTrue(response.context['current_user'].is_authenticated())
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url_for('auth.logout'), follow_redirects=True)
        self.assertFalse(response.context['current_user'].is_authenticated())
        self.assertEqual(response.status_code, 200)

    @mock.patch('flask_frontend.blueprints.auth.views.auth_blueprint.api')
    def test_register(self, api_mock):
        return_user = create_mock_for(User)
        api_mock.users.post.return_value = ApiResult(data=return_user)
        data = {'email': "dupa@dupa.com", 'password': "password", 'password_again': 'password', 'login': 'loggggin'}
        self.client.post(url_for('auth.register'), params=data)
        self.assertTrue(api_mock.users.post.called)
