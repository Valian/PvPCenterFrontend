# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import json

import requests
import urlparse

from abc import ABCMeta, abstractmethod
from requests.auth import HTTPBasicAuth
from models import Game, UnableToParseException, Errors, ModelList, User
from common.logable import Logable


class ApiException(Exception):

    def __init__(self, url, method, e):
        super(ApiException, self).__init__('error while performing {0} {1}, more info: {2}'.format(url, method, e))
        self.url = url
        self.method = method

class ApiResult(object):

    def __init__(self, data=None, errors=None):
        self.errors = errors
        self.data = data
        self.ok = not self.errors or len(errors) == 0


class ApiDispatcherBase(Logable):

    __metaclass__ = ABCMeta

    def __init__(self, base_url):
        self.base_url = base_url

    @abstractmethod
    def _make_request(self, method, endpoint, model, **kwargs):
        raise NotImplementedError

    def get_request(self, endpoint, model=None, **kwargs):
        return self._make_request('GET', endpoint, model, **kwargs)

    def post_request(self, endpoint, model=None, **kwargs):
        return self._make_request('POST', endpoint, model, **kwargs)

    def patch_request(self, endpoint, model=None, **kwargs):
        return self._make_request('PATCH', endpoint, model, **kwargs)

    def put_request(self, endpoint, model=None, **kwargs):
        return self._make_request('PUT', endpoint, model, **kwargs)

    def delete_request(self, endpoint, model=None, **kwargs):
        return self._make_request('DELETE', endpoint, model, **kwargs)


class ApiDispatcher(ApiDispatcherBase):

    def create_url(self, endpoint):
        return urlparse.urljoin(self.base_url, endpoint)

    def _make_request(self, method, endpoint, model, **kwargs):
        try:
            url = self.create_url(endpoint)
            self.log_debug("Performing {0} request to {1}".format(method, url))
            response = getattr(requests, method.lower())(url, **kwargs)
            self.log_debug("Performed {0} {1}, response code: {2}".format(url, method, response.status_code))
            return self._convert_to_api_result(model, response)
        except (ValueError, UnableToParseException) as e:
            raise ApiException(method, endpoint, e)

    @staticmethod
    def _convert_to_api_result(model, response):
        json = response.json()
        if not response.ok:
            return ApiResult(errors=Errors.from_json(json))
        else:
            return ApiResult(data=model.from_json(json) if model else json)


class PvPCenterApi(object):

    GAMES_ENDPOINT = '/games'
    GAME_ENDPOINT = '/games/{0}'
    USERS_ENDPOINT = '/users'
    USER_ENDPOINT = "/users/{0}"
    LOGIN_ENDPOINT = '/users/login'

    def __init__(self, dispatcher, login, password):
        """
        :type dispatcher: ApiDispatcherBase
        :type login: str
        :type password: str
        """
        self.dispatcher = dispatcher
        self.password = password
        self.login = login

    def get_games(self, model=ModelList.For(Game)):
        endpoint = self.GAMES_ENDPOINT
        return self.dispatcher.get_request(
            endpoint, model=model, auth=HTTPBasicAuth(self.login, self.password))

    def get_game(self, game_id, model=Game):
        endpoint = self.GAME_ENDPOINT.format(game_id)
        return self.dispatcher.get_request(endpoint, model=model, auth=HTTPBasicAuth(self.login, self.password))

    def get_users(self):
        endpoint = self.USERS_ENDPOINT
        return self.dispatcher.get_request(
            endpoint, model=ModelList.For(User), auth=HTTPBasicAuth(self.login, self.password))

    def get_user(self, user_id, model=User):
        endpoint = self.USER_ENDPOINT.format(user_id)
        return self.dispatcher.get_request(endpoint, model=model, auth=HTTPBasicAuth(self.login, self.password))

    def login_user(self, email, password, model=User):
        endpoint = self.LOGIN_ENDPOINT
        data = {'email': email, 'password': password}
        return self.dispatcher.post_request(
            endpoint, model=model, data=data, auth=HTTPBasicAuth(self.login, self.password))
