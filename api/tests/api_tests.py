# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from unittest import TestCase
import mock
import requests
from api.api import ApiDispatcher, PvPCenterApi
from api.models import ModelList, Game, User


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
            "access_token": "Ttq3SYiy-zVsy7Wm8nv4"
        }
        user = User.from_json(data)
        self.assertEqual(data['id'], user.id)
        self.assertEqual(data['nickname'], user.name)
        self.assertEqual(data['email'], user.email)
        self.assertEqual(data['access_token'], user.token)


class ApiTests(TestCase):

    url = 'http://test.com'
    login = "login"
    password = "password"

    def setUp(self):
        self.dispatcher = ApiDispatcher(self.url)
        self.api = PvPCenterApi(self.dispatcher, self.login, self.password)

    def assertConnectionError(self, api_response):
        self.assertFalse(api_response.ok)
        self.assertGreater(api_response.errors.get_errors_for_field('connection_error'), 0)

    @mock.patch('api.api.requests')
    def test_authentication(self, requests_mock):
        requests_mock.get.return_value = MockResponse({}, 200)
        api_response = self.api.get_games(model=mock.MagicMock(ModelList.For(Game)))
        self.assertIn('auth', requests_mock.get.call_args[1])
        auth = requests_mock.get.call_args[1]['auth']
        self.assertEqual(self.login, auth.username)
        self.assertEqual(self.password, auth.password)
        self.assertTrue(api_response.ok)

    @mock.patch('api.api.requests')
    def test_authentication_fail(self, requests_mock):
        requests_mock.get.side_effect = requests.HTTPError()
        api_response = self.api.get_games(model=mock.MagicMock(ModelList.For(Game)))
        self.assertConnectionError(api_response)

    @mock.patch('api.api.requests')
    def test_connection_fail(self, requests_mock):
        requests_mock.get.side_effect = requests.ConnectionError()
        api_response = self.api.get_games(model=mock.MagicMock(ModelList.For(Game)))
        self.assertConnectionError(api_response)

    @mock.patch('api.api.requests')
    def test_connection_fail(self, requests_mock):
        requests_mock.get.side_effect = ValueError()
        api_response = self.api.get_games(model=mock.MagicMock(ModelList.For(Game)))
        self.assertConnectionError(api_response)