# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
from functools import wraps
import inspect
import logging

from unittest import TestCase

from flask import url_for
from flask_classy import get_true_argspec
from flask_webtest import TestApp
import mock

from resources.core import ApiResult
from resources.mock import create_mock_for
from resources.models import User
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
    def wrapper(*args, **kwargs):
        """
        :type self: AppTestCase
        """
        self = args[0]
        get_single = prepare_patch(self, 'm_users__get_single')
        login = prepare_patch(self, 'm_users__login')
        response, user = self.login_user(get_single.start(), login.start())
        try:
            kwargs['user'] = user
            return f(*args, **kwargs)
        finally:
            get_single.stop()
            login.stop()

    return wrapper


class TestAppRedirectWrapper(TestApp):
    def __init__(self, app, *args, **kwargs):
        super(TestAppRedirectWrapper, self).__init__(app, *args, **kwargs)
        self.get = should_follow_redirect(self.get, self.get)
        self.post = should_follow_redirect(self.post, self.get)


def get_mock_target(app, name):
    if name == 'm_api':
        return app.api, app, 'api'
    name_parts = name.replace("m_", "", 1).split('__')
    parent = None
    current = app.api
    for part in name_parts:
        parent = current
        current = getattr(current, part)
    return current, parent, name_parts[-1]


def get_model_from_method(method):
    argspec = inspect.getargspec(method)
    model_arg_number = argspec.args.index("model")
    model_default_pos = model_arg_number - (len(argspec.args) - len(argspec.defaults))
    model_cls = argspec.defaults[model_default_pos]
    return model_cls


def create_repeatable_mock_for(self, model):
    self._mock_cache = getattr(self, '_mock_cache', {})
    self._mock_cache[model] = self._mock_cache.get(model, create_mock_for(model))
    return self._mock_cache[model]


def prepare_patch(self, name, **kwargs):
    target, parent, target_name = get_mock_target(self.app, name)
    if callable(target):
        model = get_model_from_method(target)
        ret_val = ApiResult(data=create_mock_for(model, **kwargs))
        patch = mock.patch.object(parent, target_name, return_value=ret_val)
    else:
        patch = mock.patch.object(parent, target_name)
    return patch


def mock_api(*names, **kwargs):
    def decorator(f):
        @wraps(f)
        def wrapper(self, *f_args, **f_kwargs):
            patches = [prepare_patch(self, name, **kwargs) for name in names]
            f_args.extend([patch.start() for patch in patches])
            try:
                return f(self, *f_args, **f_kwargs)
            finally:
                for patch in patches:
                    patch.stop()
        return wrapper
    return decorator

def auto_mock_api(f):
    @wraps(f)
    def wrapper(self, *f_args, **f_kwargs):
        argspec = get_true_argspec(f)
        patches = {name: prepare_patch(self, name) for name in argspec.args if name.startswith('m_')}
        f_kwargs.update({name: patch.start() for name, patch in patches.iteritems()})
        try:
            return f(self, *f_args, **f_kwargs)
        finally:
            for patch in patches.itervalues():
                patch.stop()
    return wrapper


class AppTestCase(TestCase):

    def get_config(self, config=None):
        return get_test_config(config)

    @classmethod
    def setUpClass(cls):
        cls._prepare_mocks_creation()

    @classmethod
    def _prepare_mocks_creation(cls):
        members = inspect.getmembers(cls, predicate=inspect.ismethod)
        valid_members = filter(lambda m: 'test' in m[0] and not m[0].startswith('_'), members)
        for name, method in valid_members:
            setattr(cls, name, auto_mock_api(method))

    def setUp(self):
        logging.getLogger().setLevel(logging.ERROR)
        config = self.get_config()
        self.app = create_app(config)
        self.client = TestAppRedirectWrapper(self.app)
        self.context = self.app.test_request_context()
        self.context.push()

    def tearDown(self):
        self.context.pop()

    def login_user(self, m_get_single, m_get_login, data=None, remember=False):
        return_user = create_mock_for(User)
        m_get_login.return_value = ApiResult(data=return_user)
        m_get_single.get_single.return_value = ApiResult(data=return_user)
        data = data or {'email': "dupa@dupa.com", 'password': "password", "remember_me": remember}
        response = self.client.post(url_for('auth.login'), params=data, follow_redirects=True)
        return response, return_user
