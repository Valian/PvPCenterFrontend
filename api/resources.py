# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from requests.auth import HTTPBasicAuth
from abc import ABCMeta

from .resource_endpoint import IndexResourceEndpoint, Endpoint, GetResourceEndpoint, Params, TokenParams, \
    CreateResourceEndpoint, PatchResourceEndpoint, DeleteResourceEndpoint
from models import Game as Game, User, UserGameOwnership, Team, TeamMembership, FriendshipInvite, Friendship, \
    Notification, TeamInvite


class Resource(object):

    __metaclass__ = ABCMeta

    @classmethod
    def create_endpoints(cls, url, *suffixes):
        urls = [Endpoint(url)]
        for suffix in suffixes:
            urls.append(Endpoint(url, suffix))
        return urls


class Games(Resource):

    def __init__(self, dispatcher, url):
        index, single = self.create_endpoints(url, '/{game_id}')
        self.get = IndexResourceEndpoint(dispatcher, index, Game)
        self.get_single = GetResourceEndpoint(dispatcher, single, Game, params=Params())


class Users(Resource):

    def __init__(self, dispatcher, url):
        index, single, login = self.create_endpoints(url, '/{user_id}', '/login')
        get_params = TokenParams('friends_of_user_id', 'strangers_to_user_id', 'nickname')
        create_data = Params('email', 'password', 'nickname')
        patch_data = Params('email', 'nationality', 'sex', 'birthdate', 'description', 'image_url')
        login_data = Params('email', 'password')
        self.get = IndexResourceEndpoint(dispatcher, index, User, params=get_params)
        self.get_single = GetResourceEndpoint(dispatcher, single, User, params=TokenParams())
        self.create = CreateResourceEndpoint(dispatcher, index, User, data_params=create_data)
        self.update = PatchResourceEndpoint(dispatcher, single, User, params=TokenParams(), data_params=patch_data)
        self.login = CreateResourceEndpoint(dispatcher, login, User, data_params=login_data)


class GameOwnerships(Resource):

    def __init__(self, dispatcher, url):
        index, single = self.create_endpoints(url, '/{game_ownership_id}')
        get_params = TokenParams('user_id')
        create_data = Params('user_id', 'game_id', 'nickname')
        update_data = Params('nickname')
        self.get = IndexResourceEndpoint(dispatcher, index, UserGameOwnership, params=get_params)
        self.create = CreateResourceEndpoint(dispatcher, index, UserGameOwnership, params=TokenParams(), data_params=create_data)
        self.update = PatchResourceEndpoint(dispatcher, single, UserGameOwnership, params=TokenParams(), data_params=update_data)
        self.delete = DeleteResourceEndpoint(dispatcher, single, params=TokenParams())


class Teams(Resource):

    def __init__(self, dispatcher, url):
        index, single = self.create_endpoints(url, '/{team_id}')
        get_params = TokenParams('name')
        create_data = Params('founder_id', 'name', 'description', 'tag')
        update_data = create_data + Params('image_url')
        self.get = IndexResourceEndpoint(dispatcher, index, Team, params=get_params)
        self.create = CreateResourceEndpoint(dispatcher, index, Team, params=TokenParams(), data_params=create_data)
        self.get_single = GetResourceEndpoint(dispatcher, single, Team, params=TokenParams())
        self.update = PatchResourceEndpoint(dispatcher, single, Team, params=TokenParams(), data_params=update_data)
        self.delete = DeleteResourceEndpoint(dispatcher, single, params=TokenParams())


class Notifications(Resource):

    def __init__(self, dispatcher, url):
        index, single = self.create_endpoints(url, '/{notification_id}')
        get_params = TokenParams('user_id')
        self.get = IndexResourceEndpoint(dispatcher, index, Notification, params=get_params)


class TeamMemberships(Resource):

    def __init__(self, dispatcher, url):
        index, single = self.create_endpoints(url, '/{team_membership_id}')
        get_params = TokenParams('team_id', 'user_id')
        create_data = Params('user_id', 'team_id')
        self.get = IndexResourceEndpoint(dispatcher, index, TeamMembership, params=get_params)
        self.create = CreateResourceEndpoint(dispatcher, index, TeamMembership, params=TokenParams(), data_params=create_data)
        self.get_single = GetResourceEndpoint(dispatcher, single, TeamMembership, params=TokenParams())
        self.update = PatchResourceEndpoint(dispatcher, single, TeamMembership, params=TokenParams(), data_params=create_data)
        self.delete = DeleteResourceEndpoint(dispatcher, single, params=TokenParams())


class TeamInvites(Resource):

    def __init__(self, dispatcher, url):
        index, single, accept = self.create_endpoints(url, '/{team_invite_id}', '/{team_invite_id}/accept')
        get_params = TokenParams('to_user_id', 'team_id')
        create_data = Params('from_user', 'team_id')
        self.get = IndexResourceEndpoint(dispatcher, index, TeamInvite, params=get_params)
        self.create = CreateResourceEndpoint(dispatcher, index, TeamInvite, params=TokenParams(), data_params=create_data)
        self.get_single = GetResourceEndpoint(dispatcher, single, TeamInvite, params=TokenParams())
        self.delete = DeleteResourceEndpoint(dispatcher, single, params=TokenParams())
        self.accept = CreateResourceEndpoint(dispatcher, accept, TeamInvite, params=TokenParams())


class FriendshipInvites(Resource):

    def __init__(self, dispatcher, url):
        index, single, accept = self.create_endpoints(url, '/{friendship_invite_id}', '/{friendship_invite_id}/accept')
        get_params = TokenParams('to_user_id', 'from_user_id')
        create_data = get_params
        self.get = IndexResourceEndpoint(dispatcher, index, FriendshipInvite, params=get_params)
        self.create = CreateResourceEndpoint(dispatcher, index, FriendshipInvite, params=TokenParams(), data_params=create_data)
        self.get_single = GetResourceEndpoint(dispatcher, single, FriendshipInvite, params=TokenParams())
        self.delete = DeleteResourceEndpoint(dispatcher, single, params=TokenParams())
        self.accept = CreateResourceEndpoint(dispatcher, accept, FriendshipInvite, params=TokenParams())


class Friendships(Resource):

    def __init__(self, dispatcher, url):
        index, single = self.create_endpoints(url, '/{friendship_id}')
        get_params = TokenParams('user_id', 'to_user_id')
        self.get = IndexResourceEndpoint(dispatcher, index, Friendship, params=get_params)
        self.delete = DeleteResourceEndpoint(dispatcher, single, params=TokenParams())


class PvPCenterApi(object):

    def __init__(self, dispatcher, login, password):
        """
        :type dispatcher: resources.core.ApiDispatcherBase
        :type login: str
        :type password: str
        """
        dispatcher.add_additional_params(auth=HTTPBasicAuth(login, password))
        self.games = Games(dispatcher, '/games')
        self.users = Users(dispatcher, '/users')
        self.game_ownerships = GameOwnerships(dispatcher, '/game_ownerships')
        self.teams = Teams(dispatcher, '/teams')
        self.team_memberships = TeamMemberships(dispatcher, '/team_memberships')
        self.team_invites = TeamInvites(dispatcher, '/team_membership_invite')
        self.friendships = Friendships(dispatcher, '/friendships')
        self.friendship_invites = FriendshipInvites(dispatcher, '/friendship_invites')
        self.notifications = Notifications(dispatcher, '/notifications')

        self._model_to_resource = {resource.get.model_cls.model: resource
                                   for resource in vars(self).itervalues() if isinstance(resource, Resource)}

    def get_model_func(self, model, funcname):
        resource = self._model_to_resource.get(model)
        if not resource:
            raise ValueError("Unable to find resource to model {0}".format(model))
        return getattr(resource, funcname)

