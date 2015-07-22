# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask
import flask_login

import mock
from unittest import TestCase
from flask import url_for
from nose_parameterized import parameterized
from api.api import ApiResult
from api.mock import UserFactory, create_mock_for
from flask_frontend.auth.user import User
from flask_frontend.app import create_app
from flask_frontend.config import get_test_config


class AuthTests(TestCase):

    def setUp(self):
        config = get_test_config()
        self.app = create_app(config)
        self.client = self.app.test_client()
        self.context = self.app.test_request_context()
        self.context.push()

    def tearDown(self):
        self.context.pop()

    def login_user(self, api_mock, data=None):
        return_user = create_mock_for(User)
        api_mock.login.post.return_value = ApiResult(data=return_user)
        api_mock.user.get.return_value = ApiResult(data=return_user)
        data = data or {'email': "dupa@dupa.com", 'password': "password"}
        response = self.client.post(url_for('auth.login'), follow_redirects=True, data=data)
        return response, return_user

    @mock.patch('flask_frontend.auth.views.auth_blueprint.api')
    def test_login(self, api_mock):
        response, user = self.login_user(api_mock)
        self.assertTrue(api_mock.login.post.called)
        self.assertIn('Logged', response.data)
        self.assertIn(user.name, response.data)

    @parameterized.expand([
        ({'email': "dupadupa.com", 'password': "password"}, 'Invalid'),
        ({'email': "dupa@dupa", 'password': "password"}, 'Invalid'),
        ({'email': "dupadupa", 'password': "password"}, 'Invalid'),
        ({'email': "", 'password': "password"}, 'Invalid'),
        ({'email': "dupa@dupa.com", 'password': ""}, 'Min'),
        ({'email': "dupa@dupa.com", 'password': "sd"}, 'Min'),
    ])
    @mock.patch('flask_frontend.auth.views.auth_blueprint.api')
    def test_invalid_email(self, data, error_message, api_mock):
        response, user = self.login_user(api_mock, data=data)
        self.assertFalse(api_mock.login.post.called)
        self.assertNotIn('Logged', response.data)
        self.assertIn(error_message, response.data)

    @mock.patch('flask_frontend.auth.views.auth_blueprint.api')
    def test_logout(self, api_mock):
        response, user = self.login_user(api_mock)
        self.assertIn('Logged', response.data)
        response = self.client.post(url_for('auth.logout'), follow_redirects=True)
        self.assertIn('Login', response.data)

    @mock.patch('flask_frontend.auth.views.auth_blueprint.api')
    def test_register(self, api_mock):
        return_user = create_mock_for(User)
        api_mock.users.post.return_value = ApiResult(data=return_user)
        data = {'email': "dupa@dupa.com", 'password': "password", 'password_again': 'password', 'login': 'loggggin'}
        self.client.post(url_for('auth.register'), data=data)
        self.assertTrue(api_mock.users.post.called)

