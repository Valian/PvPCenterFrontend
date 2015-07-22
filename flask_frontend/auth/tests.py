# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import mock
from unittest import TestCase
from flask import url_for
from api.api import ApiResult
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
        self.app.preprocess_request()

    def tearDown(self):
        self.context.pop()

    @mock.patch('flask_frontend.auth.views.auth_blueprint.api')
    def test_login(self, api_mock):
        api_mock.login.post.return_value = ApiResult(data=User(1, "kupa", "dupa@dupa.com", "aabbcc"))
        self.client.post(url_for('auth.login'), data={'email': "dupa@dupa.com", 'password': "password"})
        self.assertTrue(api_mock.login.post.called)

