# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from unittest import TestCase
from flask import url_for
from api.api import ApiResult
from api.mock import create_mock_for
from flask_frontend.blueprints.auth import User

from flask_frontend.app import create_app
from flask_frontend.config import get_test_config


class AppTestCase(TestCase):

    def get_config(self, config=None):
        return get_test_config(config)

    def setUp(self):
        config = self.get_config()
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
