# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
from _ast import Delete

import urllib

from requests import RequestException

import requests
import urlparse

from abc import ABCMeta, abstractmethod
from requests.auth import HTTPBasicAuth
from flask.ext.frontend.common.pagination import get_pagination_params
from models import Game as GameModel, Error, UnableToParseException, Errors, ModelList, User as UserModel, \
    UserGameOwnership, Team as TeamModel, TeamMembership as TeamMembershipModel, FriendshipInvite as FriendshipInviteModel, \
    Friendship, DeleteResponse, Notification, TeamInvite
from common.logable import Logable


undefined = object()


def dict_of_defined_keys(**kwargs):
    data = {}
    for key, value in kwargs.items():
        if value is not undefined:
            data[key] = value
    return data


class ApiException(Exception):

    def __init__(self, url, method, e):
        super(ApiException, self).__init__('error while performing {0} {1}, more info: {2}'.format(url, method, e))
        self.url = url
        self.method = method


class ApiResult(object):

    def __init__(self, data=None, errors=None, status=200):
        self.status = status
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
            self.log_debug("Performing {0} request to {1}. Additional: {2}".format(method, url, str(kwargs)))
            response = self._send_request(method, url, **params)
            self.log_debug("Performed {0} {1}, response code: {2}".format(url, method, response.status_code))
            return self._convert_to_api_result(model, response)
        except (UnableToParseException, RequestException, ValueError) as e:
            self.log_error("Error while performing request, more info: {0}".format(e))
            raise ApiException(endpoint, method, e)

    def create_url(self, endpoint):
        return urlparse.urljoin(self.base_url, endpoint)

    @staticmethod
    def _send_request(method, url, **kwargs):
        method = getattr(requests, method.lower())
        return method(url, **kwargs)

    def _convert_to_api_result(self, model, response):
        json = response.json()
        self.log_debug('Response data: {0}'.format(json))
        if not response.ok:
            return ApiResult(errors=Errors.from_json(json), status=response.status_code)
        else:
            return ApiResult(data=model.from_json(json) if model else json, status=response.status_code)


class Resource(object):

    __metaclass__ = ABCMeta

    def __init__(self, dispatcher, url):
        self.dispatcher = dispatcher
        self.url = url

    def create_url(self, suffix="", params=None, **kwargs):
        url = (self.url + suffix).format(**kwargs)
        if params:
            url = url + '?{0}'.format(urllib.urlencode(params))
        return url

    def create_url_with_pagination(self, suffix="", params=None, **kwargs):
        page, per_page = get_pagination_params()
        params = params or {}
        params.update(offset=(page - 1) * per_page, limit=per_page)
        return self.create_url(suffix, params, **kwargs)

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

    SINGLE_ENDPOINT = "/{game_id}"

    def get(self, model=ModelList.For(GameModel)):
        endpoint = self.create_url_with_pagination()
        return self._get_request(endpoint, model=model)

    def get_single(self, game_id, model=GameModel):
        endpoint = self.create_url(suffix=self.SINGLE_ENDPOINT, game_id=game_id)
        return self._get_request(endpoint, model=model)


class Users(Resource):

    SINGLE_ENDPOINT = "/{user_id}"
    LOGIN_ENDPOINT = "/login"

    def get(self, token=undefined, friends_of_user_id=undefined, nickname=undefined, strangers_to_user_id=undefined,
            model=ModelList.For(UserModel)):
        token = token or undefined
        params = dict_of_defined_keys(
            friends_of_user_id=friends_of_user_id, strangers_to_user_id=strangers_to_user_id, nickname=nickname,
            access_token=token)
        endpoint = self.create_url_with_pagination(params=params)
        return self._get_request(endpoint, model=model)

    def post(self, login, email, password, model=UserModel):
        endpoint = self.create_url()
        data = {'nickname': login, 'email': email, 'password': password}
        return self._post_request(endpoint, data=data, model=model)

    def get_single(self, user_id, token=undefined, model=UserModel):
        params = dict_of_defined_keys(access_token=token or undefined)
        endpoint = self.create_url(suffix=self.SINGLE_ENDPOINT, user_id=user_id, params=params)
        return self._get_request(endpoint, model=model)

    def patch(self, user_id, token, email=undefined, nationality=undefined, sex=undefined, birthdate=undefined,
              description=undefined, image_url=undefined, model=UserModel):
        params = {"access_token": token}
        data = dict_of_defined_keys(
            email=email, nationality=nationality, sex=sex, birthdate=birthdate, description=description,
            image_url=image_url)
        endpoint = self.create_url(suffix=self.SINGLE_ENDPOINT, params=params, user_id=user_id)
        return self._patch_request(endpoint, model=model, data=data)

    def login(self, email, password, model=UserModel):
        endpoint = self.create_url(suffix=self.LOGIN_ENDPOINT)
        data = {'email': email, 'password': password}
        return self._post_request(endpoint, model=model, data=data)


class GameOwnerships(Resource):

    SINGLE_ENDPOINT = "/{game_ownership_id}"

    def get(self, id, token, model=ModelList.For(UserGameOwnership)):
        params = {"user_id": id, "access_token": token}
        endpoint = self.create_url_with_pagination(params=params)
        return self._get_request(endpoint, model=model)

    def create(self, token, user_id, game_id, nickname, model=UserGameOwnership):
        data = {'user_id': user_id, 'game_id': game_id, 'nickname': nickname}
        params = {'access_token': token}
        endpoint = self.create_url(params=params)
        return self._post_request(endpoint, model=model, data=data)

    def update(self, token, game_ownership_id, nickname, model=UserGameOwnership):
        data = {'nickname': nickname}
        params = {'access_token': token}
        endpoint = self.create_url(self.SINGLE_ENDPOINT, game_ownership_id=game_ownership_id, params=params)
        return self._patch_request(endpoint, model, data=data)


class Teams(Resource):

    SINGLE_ENDPOINT = "/{team_id}"

    def get(self, name=undefined, model=ModelList.For(TeamModel)):
        params = dict_of_defined_keys(name=name)
        endpoint = self.create_url_with_pagination(params=params)
        return self._get_request(endpoint, model=model)

    def post(self, token, name, description, tag, model=TeamModel):
        endpoint = self.create_url(params={"access_token": token})
        data = {'name': name, 'description': description, 'tag': tag}
        return self._post_request(endpoint, model=model, data=data)

    def get_single(self, team_id, model=TeamModel):
        endpoint = self.create_url(suffix=self.SINGLE_ENDPOINT, team_id=team_id)
        return self._get_request(endpoint, model=model)

    def patch(self, team_id, token, name=undefined, description=undefined, tag=undefined, founder_id=undefined,
              model=TeamModel):
        endpoint = self.create_url(suffix=self.SINGLE_ENDPOINT, team_id=team_id, params={"access_token": token})
        data = dict_of_defined_keys(name=name, description=description, tag=tag, founder_id=founder_id)
        return self._patch_request(endpoint, model=model, data=data)


class Notifications(Resource):

    def get(self, token, user_id, model=ModelList.For(Notification)):
        params = {"access_token": token, "user_id": user_id}
        endpoint = self.create_url_with_pagination(params=params)
        return self._get_request(endpoint, model=model)


class TeamMemberships(Resource):

    SINGLE_ENDPOINT = "/{team_membership_id}"

    def get(self, team_id=undefined, user_id=undefined, model=ModelList.For(TeamMembershipModel)):
        params = dict_of_defined_keys(team_id=team_id, user_id=user_id)
        endpoint = self.create_url_with_pagination(params=params)
        return self._get_request(endpoint, model=model)

    def get_single(self, team_membership_id, model=TeamMembershipModel):
        endpoint = self.create_url(suffix=self.SINGLE_ENDPOINT, team_membership_id=team_membership_id)
        return self._get_request(endpoint, model=model)

    def create(self, token, user_id, team_id, model=TeamMembershipModel):
        data = {'user_id': user_id, 'team_id': team_id}
        endpoint = self.create_url(params={'access_token': token})
        return self._post_request(endpoint, model=model, data=data)

    def patch(self, token, team_membership_id, user_id=undefined, team_id=undefined, model=TeamMembershipModel):
        data = dict_of_defined_keys(user_id=user_id, team_id=team_id)
        endpoint = self.create_url(
            suffix=self.SINGLE_ENDPOINT, team_membership_id=team_membership_id, params={'access_token': token})
        return self._patch_request(endpoint, model=model, data=data)


class TeamInvites(Resource):

    SINGLE_ENDPOINT = "/{team_invite_id}"
    ACCEPT_ENDPOINT = "/{team_invite_id}/accept"

    def get(self, to_user_id=undefined, team_id=undefined, model=ModelList.For(TeamInvite)):
        params = dict_of_defined_keys(to_user_id=to_user_id, team_id=team_id)
        endpoint = self.create_url_with_pagination(params=params)
        return self._get_request(endpoint, model=model)

    def get_single(self, team_invite_id, model=TeamMembershipModel):
        endpoint = self.create_url(suffix=self.SINGLE_ENDPOINT, team_invite_id=team_invite_id)
        return self._get_request(endpoint, model=model)

    def create(self, token, user_id, team_id, model=TeamMembershipModel):
        data = {'from_user': user_id, 'team_id': team_id}
        endpoint = self.create_url(params={'access_token': token})
        return self._post_request(endpoint, model=model, data=data)

    def delete(self, team_invite_id, token, model=DeleteResponse):
        endpoint = self.create_url(
            suffix=self.SINGLE_ENDPOINT, team_invite_id=team_invite_id, params={'access_token': token})
        return self._delete_request(endpoint, model)

    def accept(self, team_invite_id, token, model=FriendshipInviteModel):
        endpoint = self.create_url(
            suffix=self.ACCEPT_ENDPOINT, team_invite_id=team_invite_id, params={'access_token': token})
        return self._post_request(endpoint, model, data={})


class FriendshipInvites(Resource):
    
    SINGLE_ENDPOINT = "/{friendship_invite_id}"
    ACCEPT_ENDPOINT = "/{friendship_invite_id}/accept"

    def get(self, token, to_user_id, from_user_id=undefined, model=ModelList.For(FriendshipInviteModel)):
        params = dict_of_defined_keys(access_token=token, to_user_id=to_user_id, from_user_id=from_user_id)
        endpoint = self.create_url_with_pagination(params=params)
        return self._get_request(endpoint, model)

    def get_single(self, friendship_invite_id, token, model=FriendshipInviteModel):
        endpoint = self.create_url(
            suffix=self.SINGLE_ENDPOINT, friendship_invite_id=friendship_invite_id, params={'access_token': token})
        return self._get_request(endpoint, model)

    def create(self, token, from_user_id, to_user_id, model=FriendshipInviteModel):
        data = {'from_user_id': from_user_id, 'to_user_id': to_user_id}
        endpoint = self.create_url(params={'access_token': token})
        return self._post_request(endpoint, model=model, data=data)

    def delete(self, friendship_invite_id, token, model=DeleteResponse):
        endpoint = self.create_url(
            suffix=self.SINGLE_ENDPOINT, friendship_invite_id=friendship_invite_id, params={'access_token': token})
        return self._delete_request(endpoint, model)

    def accept(self, friendship_invite_id, token, model=FriendshipInviteModel):
        endpoint = self.create_url(
            suffix=self.ACCEPT_ENDPOINT, friendship_invite_id=friendship_invite_id, params={'access_token': token})
        return self._post_request(endpoint, model, data={})


class Friendships(Resource):

    SINGLE_ENDPOINT = "/{friendship_id}"

    def get(self, token, user_id, to_user_id=undefined, model=ModelList.For(Friendship)):
        params = dict_of_defined_keys(access_token=token, user_id=user_id, to_user_id=to_user_id)
        endpoint = self.create_url_with_pagination(params=params)
        return self._get_request(endpoint, model)

    def delete(self, token, friendship_id, model=DeleteResponse):
        endpoint = self.create_url(
            suffix=self.SINGLE_ENDPOINT, friendship_id=friendship_id, params={'access_token': token})
        return self._delete_request(endpoint, model)


class PvPCenterApi(object):

    GAMES_ENDPOINT = '/games'
    USERS_ENDPOINT = '/users'
    GAME_OWNERSHIPS_ENDPOINT = '/game_ownerships'
    TEAMS_ENDPOINT = '/teams'
    TEAM_MEMBERSHIPS_ENDPOINT = '/team_memberships'
    TEAM_INVITE_ENDPOINT = '/team_membership_invite'
    FRIENDSHIPS_ENDPOINT = '/friendships'
    FRIENDSHIP_INVITES_ENDPOINT = '/friendship_invites'
    NOTIFICATIONS_ENDPOINT = '/notifications'

    def __init__(self, dispatcher, login, password):
        """
        :type dispatcher: ApiDispatcherBase
        :type login: str
        :type password: str
        """
        dispatcher.add_additional_params(auth=HTTPBasicAuth(login, password))
        self.games = Games(dispatcher, self.GAMES_ENDPOINT)
        self.users = Users(dispatcher, self.USERS_ENDPOINT)
        self.game_ownerships = GameOwnerships(dispatcher, self.GAME_OWNERSHIPS_ENDPOINT)
        self.teams = Teams(dispatcher, self.TEAMS_ENDPOINT)
        self.team_memberships = TeamMemberships(dispatcher, self.TEAM_MEMBERSHIPS_ENDPOINT)
        self.team_invites = TeamInvites(dispatcher, self.TEAM_INVITE_ENDPOINT)
        self.friendships = Friendships(dispatcher, self.FRIENDSHIPS_ENDPOINT)
        self.friendship_invites = FriendshipInvites(dispatcher, self.FRIENDSHIP_INVITES_ENDPOINT)
        self.notifications = Notifications(dispatcher, self.NOTIFICATIONS_ENDPOINT)



