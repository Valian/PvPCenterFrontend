# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
from functools import wraps
import logging
from unittest import TestCase

from flask import url_for

from flask_webtest import TestApp
import mock

from api.core import ApiResult
from api.mock import create_mock_for
from api.models import User
from flask_frontend.app import create_app
from flask_frontend.config import get_test_config


class TestAppRedirectWrapper(TestApp):
    def __init__(self, app, *args, **kwargs):
        super(TestAppRedirectWrapper, self).__init__(app, *args, **kwargs)
        self.get = should_follow_redirect(self.get, self.get)
        self.post = should_follow_redirect(self.post, self.get)


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


def logged_in(**attrs):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            """
            :type self: AppTestCase
            """
            self = args[0]
            get_single = create_patch(self.app.api, User, 'get_single')
            login = create_patch(self.app.api, User, 'login')
            response, user = self.login_user(get_single.start(), login.start(), **attrs)
            try:
                kwargs['user'] = user
                return f(*args, **kwargs)
            finally:
                get_single.stop()
                login.stop()
        return wrapper
    return decorator


def create_patch(api, model, method, model_kwargs=None, exception=None):
    resource = api.get_model_resource(model)
    model = getattr(resource, method).model_cls
    if exception:
        return mock.patch.object(resource, method, side_effect=exception)
    result = ApiResult(data=create_mock_for(model, **(model_kwargs or {})))
    return mock.patch.object(resource, method, return_value=result)


def mock_api(model, method, exception=None, **kwargs):
    def decorator(f):
        @wraps(f)
        def wrapper(self, *f_args, **f_kwargs):
            with create_patch(self.app.api, model, method, kwargs, exception) as mock_resource:
                f_args = list(f_args)
                f_args.append(mock_resource)
                return f(self, *f_args, **f_kwargs)
        return wrapper
    return decorator


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

    def login_user(self, get_single, login, data=None, remember=False, **kwargs):
        return_user = create_mock_for(User, **kwargs)
        login.return_value = ApiResult(data=return_user)
        get_single.return_value = ApiResult(data=return_user)
        data = data or {'email': "dupa@dupa.com", 'password': "password", "remember_me": remember}
        response = self.client.post(url_for('auth.login'), params=data, follow_redirects=True)
        return response, return_user
