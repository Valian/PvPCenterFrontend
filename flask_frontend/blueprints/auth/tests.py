# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import mock
from flask import url_for

from api.models import User
from flask_frontend.common.app_test_case import AppTestCase, mock_api


class AuthTests(AppTestCase):

    @mock_api(User, 'login')
    @mock_api(User, 'get_single')
    def test_login(self, login, single):
        response, user = self.login_user(single, login)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(login.called)
        self.assertIn('Logout', response.body)
        logged_user = response.context['current_user']
        self.assertEqual(single.return_value.data, logged_user)
        self.assertTrue(logged_user.is_authenticated())

    @mock_api(User, 'login')
    @mock_api(User, 'get_single')
    @mock.patch('flask_frontend.blueprints.auth.views.flask_login')
    def test_login_remember_me(self, login, single, login_mock):
        response, user = self.login_user(single, login, remember=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(login.called)
        self.assertEqual(mock.call(user, remember=True), login_mock.login_user.call_args)

    @mock_api(User, 'login')
    @mock_api(User, 'get_single')
    def test_logout(self, login, single):
        response = self.client.get(url_for('index'))
        self.assertFalse(response.context['current_user'].is_authenticated())
        self.assertEqual(response.status_code, 200)
        response, user = self.login_user(single, login)
        self.assertTrue(response.context['current_user'].is_authenticated())
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url_for('auth.logout'), follow_redirects=True)
        self.assertFalse(response.context['current_user'].is_authenticated())
        self.assertEqual(response.status_code, 200)

    @mock_api(User, 'create')
    def test_register(self, create):
        data = {'email': "dupa@dupa.com", 'password': "password", 'password_again': 'password', 'nickname': 'loggggin'}
        self.client.post(url_for('auth.register'), params=data)
        self.assertTrue(create.called)
