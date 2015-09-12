# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
from functools import wraps
import logging

from unittest import TestCase

from flask import url_for
from flask_webtest import TestApp
import mock

from api.api import ApiResult
from api.mock import create_mock_for
from flask_frontend.blueprints.auth import User
from flask_frontend.app import create_app
from flask_frontend.config import get_test_config


def should_follow_redirect(f, callback):
    @wraps(f)
    def wrapper(*args, **kwargs):
        follow_redirects = kwargs.pop('follow_redirects', False)
        response = f(*args, **kwargs)
        if response.status_code == 302 and follow_redirects:
            location = filter(lambda h: h[0] == 'Location', response.headerlist)[0][1]
            return callback(location)
        return response
    return wrapper


def logged_in(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        """
        :type self: AppTestCase
        """
        with mock.patch('flask_frontend.blueprints.auth.views.auth_blueprint.api') as auth_mock:
            _, user = self.login_user(auth_mock)
            return f(self, user, *args, **kwargs)
    return wrapper


class TestAppRedirectWrapper(TestApp):
    def __init__(self, app, *args, **kwargs):
        super(TestAppRedirectWrapper, self).__init__(app, *args, **kwargs)
        self.get = should_follow_redirect(self.get, self.get)
        self.post = should_follow_redirect(self.post, self.get)


class AppTestCase(TestCase):

    def get_config(self, config=None):
        return get_test_config(config)

    def setUp(self):
        logging.getLogger().setLevel(logging.ERROR)
        config = self.get_config()
        self.app = create_app(config)
        self.client = TestAppRedirectWrapper(self.app)
        self.context = self.app.test_request_context()
        self.context.push()

    def tearDown(self):
        self.context.pop()

    def login_user(self, api_mock, data=None, remember=False):
        return_user = create_mock_for(User)
        api_mock.users.login.return_value = ApiResult(data=return_user)
        api_mock.users.get_single.return_value = ApiResult(data=return_user)
        data = data or {'email': "dupa@dupa.com", 'password': "password", "remember_me": remember}
        response = self.client.post(url_for('auth.login'), params=data, follow_redirects=True)
        return response, return_user
