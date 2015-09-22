# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask import url_for
import mock

from resources.resources import ApiResult
from resources.core import ApiException, ApiResult
from resources.mock import TeamFactory, UserFactory, TeamMembershipFactory, create_mock_for
from resources.models import ModelList, TeamMembership, Team
from flask_frontend.common.app_test_case import AppTestCase, logged_in


@mock.patch('flask_frontend.blueprints.teams.views.teams_blueprint.api')
class TeamTests(AppTestCase):

    def test_teams_view_calls_api(self, api):
        response = self.client.get(url_for('teams.teams_view'))
        self.assertEqual(api.teams.get.call_count, 1)
        self.assertEqual(response.context['teams'], )

    def test_teams_500_on_api_error(self, api):
        api.teams.get.side_effect = ApiException("url", "method", Exception())
        self.client.get(url_for('teams.teams_view'), expect_errors=True)

    def test_team_view_calls_api(self, api):
        team = create_mock_for(Team)
        count = team.member_count
        memberships = create_mock_for(ModelList.For(TeamMembership), count)
        api.teams.get_single.return_value = ApiResult(data=team)
        api.team_memberships.get.return_value = ApiResult(data=memberships)
        response = self.client.get(url_for('teams.team_view', team_id=team.id))
        self.assertEqual(api.teams.get_single.call_count, 1)
        self.assertEqual(api.team_memberships.get.call_count, 1)
        self.assertEqual(response.context['team'], team)
        self.assertEqual(response.context['members'], [m.user for m in memberships])

    def test_team_500_on_api_error(self, api):
        api.teams.get_single.side_effect = ApiException("url", "method", Exception())
        api.team_memberships.get.side_effect = ApiException("url", "method", Exception())
        self.client.get(url_for('teams.team_view', team_id=1), expect_errors=True)

    @logged_in
    def test_create_new_team(self, user, api):
        team = create_mock_for(Team)
        api.teams.create.return_value = ApiResult(data=team)
        body = {'name': 'Heheheh', 'tag': 'TAG', 'description': 'description'}
        response = self.client.post(url_for('teams.create_team_view'), params=body)
        self.assertLess(response.status_code, 400)
        expected_call = mock.call(user.token, user.id, body['name'], body['description'], body['tag'])
        self.assertEqual(api.teams.create.call_args, expected_call)

    @logged_in
    def test_edit_team_data(self, user, api):
        team = create_mock_for(Team, founder__id=user.id)
        api.teams.get_single.return_value = ApiResult(data=team)
        body = {'name': 'Heheheh', 'tag': 'TAG', 'description': 'description'}
        response = self.client.post(url_for('teams.change_basic', team_id=team.id), params=body)
        self.assertLess(response.status_code, 400)
        expected_call = mock.call(
            team.id, user.token, name=body['name'], description=body['description'], tag=body['tag'])
        self.assertEqual(api.teams.patch.call_args, expected_call)
