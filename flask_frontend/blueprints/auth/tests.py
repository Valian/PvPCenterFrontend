# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import mock
from flask import url_for
from nose_parameterized import parameterized

from api.api import ApiResult
from api.mock import create_mock_for
from flask_frontend.common.app_test_case import AppTestCase


class AuthTests(AppTestCase):

    def test_login(self, m_users__get_single, m_users__login):
        response, user = self.login_user(m_users__get_single, m_users__login)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(m_users__login.called)
        self.assertIn('Logout', response.body)
        logged_user = response.context['current_user']
        self.assertEqual(m_users__get_single.return_value.data, logged_user)
        self.assertTrue(logged_user.is_authenticated())

    @mock.patch('flask_frontend.blueprints.auth.views.flask_login')
    def test_login_remember_me(self, login_mock, m_users__get_single, m_users__login):
        response, user = self.login_user(m_users__get_single, m_users__login, remember=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(m_users__login.called)
        self.assertEqual(mock.call(user, remember=True), login_mock.login_user.call_args)

    def test_logout(self, m_users__get_single, m_users__login):
        response = self.client.get(url_for('index'))
        self.assertFalse(response.context['current_user'].is_authenticated())
        self.assertEqual(response.status_code, 200)
        response, user = self.login_user(m_users__get_single, m_users__login)
        self.assertTrue(response.context['current_user'].is_authenticated())
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url_for('auth.logout'), follow_redirects=True)
        self.assertFalse(response.context['current_user'].is_authenticated())
        self.assertEqual(response.status_code, 200)

    def test_register(self, m_users__create):
        data = {'email': "dupa@dupa.com", 'password': "password", 'password_again': 'password', 'nickname': 'loggggin'}
        self.client.post(url_for('auth.register'), params=data)
        self.assertTrue(m_users__create.called)
