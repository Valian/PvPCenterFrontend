# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from unittest import TestCase

import mock
import requests
from nose_parameterized import parameterized
from api.core import ApiDispatcher, ApiException
from api.models import User, UnableToParseException, Game, ModelBase, ModelList
from api.resources import PvPCenterApi


class MockResponse(object):

    def __init__(self, data, status_code):
        self.data = data
        self.status_code = status_code
        self.ok = status_code < 400

    def json(self):
        return self.data


class ModelTests(TestCase):

    def test_create_game(self):
        data = {'id': 11, 'name': "test"}
        game = Game.from_json(data)
        self.assertEqual(data['id'], game.id)
        self.assertEqual(data['name'], game.name)

    def test_create_user(self):
        data = {
            "id": 35,
            "email": "test@test.com",
            "nickname": "testtest",
            "settings_mask": 0,
            "access_token": "Ttq3SYiy-zVsy7Wm8nv4",
            "ranking": 125
        }
        user = User.from_json(data)
        self.assertEqual(data['id'], user.id)
        self.assertEqual(data['nickname'], user.name)
        self.assertEqual(data['email'], user.email)
        self.assertEqual(data['access_token'], user.token)
        self.assertEqual(data['ranking'], user.ranking)

    @parameterized.expand([(None,), ([],), ({},), ({'test': 'test'},)])
    def test_bad_data(self, data):
        self.assertRaises(UnableToParseException, lambda: User.from_json(data))


class DispatcherTests(TestCase):

    url = 'http://test.com'
    login = "login"
    password = "password"

    def setUp(self):
        self.dispatcher = ApiDispatcher(self.url)

    @parameterized.expand([('GET',), ('POST',), ('DELETE',), ('PATCH',), ('PUT',)])
    @mock.patch('api.api.requests')
    def test_requests(self, method, requests_mock):
        mock_method = getattr(requests_mock, method.lower())
        mock_method.return_value = MockResponse({}, 200)
        self.dispatcher.make_request(method, '/test', model=mock.MagicMock(ModelBase))
        self.assertTrue(mock_method.called)
        self.assertIn(self.url + '/test', mock_method.call_args[0])

    @mock.patch('api.api.requests')
    def test_with_arguments(self, requests_mock):
        requests_mock.get.return_value = MockResponse({}, 200)
        args = {'arg1': '1', 'arg2': '2'}
        self.dispatcher.add_additional_params(**args)
        self.dispatcher.make_request('GET', '/test', model=mock.MagicMock(ModelBase))
        for name, val in args.iteritems():
            self.assertIn(name, requests_mock.get.call_args[1])
            self.assertEqual(val, requests_mock.get.call_args[1][name])


class ApiTests(TestCase):

    url = 'http://test.com'
    login = "login"
    password = "password"

    def setUp(self):
        self.dispatcher = ApiDispatcher(self.url)
        self.api = PvPCenterApi(self.dispatcher, self.login, self.password)

    @mock.patch('api.api.requests')
    def test_authentication(self, requests_mock):
        requests_mock.get.return_value = MockResponse({}, 200)
        api_response = self.api.games.get(model=mock.MagicMock(ModelList.For(Game)))
        self.assertIn('auth', requests_mock.get.call_args[1])
        auth = requests_mock.get.call_args[1]['auth']
        self.assertEqual(self.login, auth.username)
        self.assertEqual(self.password, auth.password)
        self.assertTrue(api_response.ok)

    @parameterized.expand([
        (requests.ConnectionError(),),
        (ValueError(),),
        (requests.HTTPError(),)])
    @mock.patch('api.api.requests')
    def test_various_exceptions(self, exception, requests_mock):
        requests_mock.get.side_effect = exception
        self.assertRaises(ApiException, lambda: self.api.games.get(model=mock.MagicMock(ModelList.For(Game))))

    @mock.patch('api.api.requests')
    def test_error_response(self, requests_mock):
        error_data = {'some_error': ['1', '2'], 'other_error': ['1']}
        requests_mock.get.return_value = MockResponse(error_data, 500)
        api_response = self.api.games.get(model=mock.MagicMock(ModelList.For(Game)))
        self.assertFalse(api_response.ok)
        self.assertEqual(len(api_response.errors), len(error_data))
        for key, errors in error_data.iteritems():
            errors_for_field = map(lambda e: e.message, api_response.errors.get_errors_for_field(key))
            for error in errors:
                self.assertIn(error, errors_for_field)


