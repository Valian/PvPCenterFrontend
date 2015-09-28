# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask import url_for
import mock
from api.constants import TEAM_PROPOSITION_TYPE

from api.core import ApiException, ApiResult
from api.mock import create_mock_for
from api.models import ModelList, TeamMembership, Team, TeamProposition
from flask_frontend.common.app_test_case import AppTestCase, logged_in, mock_api


class TeamTests(AppTestCase):

    @mock_api(Team, 'get')
    def test_teams_view_calls_api(self, get):
        response = self.client.get(url_for('teams.teams_view'))
        self.assertEqual(get.call_count, 1)
        self.assertEqual(response.context['teams'], get.return_value.data)

    @mock_api(Team, 'get', exception=ApiException('test', 'test', None))
    def test_teams_500_on_api_error(self, get):
        response = self.client.get(url_for('teams.teams_view'), expect_errors=True)
        self.assertEqual(response.status_code, 500)

    @mock_api(Team, 'get_single')
    def test_team_view_calls_api(self, get_single):
        response = self.client.get(url_for('teams.team_view', team_id=1))
        self.assertEqual(get_single.call_count, 1)
        self.assertEqual(response.context['team'], get_single.return_value.data)

    @mock_api(Team, 'get_single', exception=ApiException('test', 'test', None))
    def test_team_500_on_api_error(self, get_single):
        response = self.client.get(url_for('teams.team_view', team_id=1), expect_errors=True)
        self.assertEqual(response.status_code, 500)

    @mock_api(TeamMembership, 'get')
    def test_members_view_calls_api(self, get):
        response = self.client.get(url_for('teams.members_view', team_id=1))
        self.assertEqual(get.call_count, 1)
        self.assertEqual(response.context['memberships'], get.return_value.data)

    @mock_api(TeamProposition, 'create')
    @logged_in()
    def test_propose_user_to_team_calls_api(self, create, user):
        body = {'team_id': 5, 'user_id': 13, 'type': TEAM_PROPOSITION_TYPE.INVITE}
        response = self.client.post(url_for('teams.propose_user'), params=body, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(create.call_args, mock.call(
            token=user.token, team_id=body['team_id'], user_id=body['user_id'], type=body['type']))

    @mock_api(TeamProposition, 'accept')
    @mock_api(TeamProposition, 'get', user__id=5, team__id=10, list_count=1)
    @logged_in()
    def test_accept_invite_calls_api(self, accept, get, user):
        data = {'user_id': 5, 'team_id': 10}
        response = self.client.post(url_for('teams.accept_proposition'), params=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(accept.call_args, mock.call(token=user.token, team_proposition_id=get.return_value.data[0].id))

    @mock_api(TeamProposition, 'delete')
    @mock_api(TeamProposition, 'get', user__id=5, team__id=10, list_count=1)
    @logged_in()
    def test_decline_invite_calls_api(self, delete, get, user):
        data = {'user_id': 5, 'team_id': 10}
        response = self.client.post(url_for('teams.decline_proposition'), params=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(delete.call_args, mock.call(token=user.token, team_proposition_id=get.return_value.data[0].id))

    @mock_api(TeamMembership, 'get', list_count=1, id=123)
    @mock_api(TeamMembership, 'delete')
    @mock_api(Team, 'get_single')
    @logged_in()
    def test_remove_member_calls_api(self, get, delete, get_single, user):
        get_single.return_value.data.founder = user
        data = {'team_id': 1, 'user_id': 3}
        response = self.client.post(url_for('teams.remove_from_team'), params=data)
        self.assertEqual(delete.call_count, 1)
        self.assertEqual(delete.call_args, mock.call(token=user.token, team_membership_id=123))

    @mock_api(Team, 'create')
    @logged_in()
    def test_create_new_team(self, create, user):
        body = {'name': 'Heheheh', 'tag': 'TAG', 'description': 'description'}
        response = self.client.post(url_for('teams.create_team_view'), params=body)
        self.assertLess(response.status_code, 400)
        expected_call = mock.call(token=user.token, founder_id=user.id, name=body['name'], description=body['description'], tag=body['tag'])
        self.assertEqual(create.call_args, expected_call)

    @mock_api(Team, 'update')
    @mock_api(Team, 'get_single')
    @logged_in()
    def test_edit_team_data(self, update, get_single, user):
        team = get_single.return_value.data
        team.founder = user
        body = {'name': 'Heheheh', 'tag': 'TAG', 'description': 'description'}
        response = self.client.post(url_for('teams.change_basic', team_id=team.id), params=body)
        self.assertLess(response.status_code, 400)
        expected_call = mock.call(
            team_id=team.id, token=user.token, name=body['name'], description=body['description'],
            tag=body['tag'])
        self.assertEqual(update.call_args, expected_call)

