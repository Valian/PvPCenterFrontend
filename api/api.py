# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from requests import RequestException

import requests
import urlparse

from abc import ABCMeta, abstractmethod
from requests.auth import HTTPBasicAuth
from models import Game as GameModel, Error, UnableToParseException, Errors, ModelList, User as UserModel, \
    UserGameOwnership
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

    def __init__(self, base_url, additional_params=None):
        self.base_url = base_url
        self.additional_params = additional_params or {}

    def add_additional_params(self, **kwargs):
        self.additional_params.update(kwargs)

    @abstractmethod
    def make_request(self, method, endpoint, model, **kwargs):
        raise NotImplementedError


class ApiDispatcher(ApiDispatcherBase):

    def make_request(self, method, endpoint, model, **kwargs):
        try:
            url = self.create_url(endpoint)
            params = dict(self.additional_params)
            params.update(kwargs)
            self.log_debug("Performing {0} request to {1}".format(method, url))
            response = self._send_request(method, url, **params)
            self.log_debug("Performed {0} {1}, response code: {2}".format(url, method, response.status_code))
            return self._convert_to_api_result(model, response)
        except (UnableToParseException, RequestException, ValueError) as e:
            raise ApiException(endpoint, method, e)

    def create_url(self, endpoint):
        return urlparse.urljoin(self.base_url, endpoint)

    @staticmethod
    def _send_request(method, url, **kwargs):
        method = getattr(requests, method.lower())
        return method(url, **kwargs)

    @staticmethod
    def _convert_to_api_result(model, response):
        json = response.json()
        if not response.ok:
            return ApiResult(errors=Errors.from_json(json))
        else:
            return ApiResult(data=model.from_json(json) if model else json)


class Resource(object):

    __metaclass__ = ABCMeta

    def __init__(self, dispatcher, url):
        self.dispatcher = dispatcher
        self.url = url

    def create_url(self, **kwargs):
        return self.url.format(**kwargs)

    def _get_request(self, endpoint, model=None, **kwargs):
        return self.dispatcher.make_request('GET', endpoint, model, **kwargs)

    def _post_request(self, endpoint, model=None, **kwargs):
        return self.dispatcher.make_request('POST', endpoint, model, **kwargs)

    def _patch_request(self, endpoint, model=None, **kwargs):
        return self.dispatcher.make_request('PATCH', endpoint, model, **kwargs)

    def _put_request(self, endpoint, model=None, **kwargs):
        return self.dispatcher.make_request('PUT', endpoint, model, **kwargs)

    def _delete_request(self, endpoint, model=None, **kwargs):
        return self.dispatcher.make_request('DELETE', endpoint, model, **kwargs)


class Games(Resource):

    def get(self, model=ModelList.For(GameModel)):
        endpoint = self.create_url()
        return self._get_request(endpoint, model=model)


class Game(Resource):

    def get(self, game_id, model=GameModel):
        endpoint = self.create_url(game_id=game_id)
        return self._get_request(endpoint, model=model)


class Users(Resource):

    def get(self, model=ModelList.For(UserModel)):
        endpoint = self.create_url()
        return self._get_request(endpoint, model=model)

    def post(self, login, email, password, model=UserModel):
        endpoint = self.create_url()
        data = {'login': login, 'email': email, 'password': password}
        return self._post_request(endpoint, data=data, model=model)


class User(Resource):

    def get(self, user_id, model=UserModel):
        endpoint = self.create_url(user_id=user_id)
        return self._get_request(endpoint, model=model)


class Login(Resource):

    def post(self, email, password, model=UserModel):
        endpoint = self.create_url()
        data = {'email': email, 'password': password}
        return self._post_request(endpoint, model=model, data=data)


class GameOwnerships(Resource):

    def get(self, id, token, model=ModelList.For(UserGameOwnership)):
        endpoint = self.create_url(user_id=id, token=token)
        return self._get_request(endpoint, model=model)


class PvPCenterApi(object):

    GAMES_ENDPOINT = '/games'
    USERS_ENDPOINT = '/users'
    GAME_OWNERSHIPS_ENDPOINT = '/game_ownerships'

    def __init__(self, dispatcher, login, password):
        """
        :type dispatcher: ApiDispatcherBase
        :type login: str
        :type password: str
        """
        dispatcher.add_additional_params(auth=HTTPBasicAuth(login, password))
        self.game = Game(dispatcher, self.GAMES_ENDPOINT + '/{game_id}')
        self.games = Games(dispatcher, self.GAMES_ENDPOINT)
        self.users = Users(dispatcher, self.USERS_ENDPOINT)
        self.user = User(dispatcher, self.USERS_ENDPOINT + '/{user_id}')
        self.login = Login(dispatcher, self.USERS_ENDPOINT + '/login')
        self.game_ownerships = GameOwnerships(
            dispatcher, self.GAME_OWNERSHIPS_ENDPOINT + '?access_token={token}&user_id={user_id}')

