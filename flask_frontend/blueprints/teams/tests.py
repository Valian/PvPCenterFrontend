# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask import url_for
import mock

from api.api import ApiResult, ApiException
from api.mock import TeamFactory, UserFactory, TeamMembershipFactory
from flask_frontend.common.app_test_case import AppTestCase


@mock.patch('flask_frontend.blueprints.teams.views.teams_blueprint.api')
class TeamTests(AppTestCase):

    def test_teams_view_calls_api(self, api):
        count = 10
        teams = [TeamFactory() for _ in xrange(count)]
        api.teams.get.return_value = ApiResult(data=teams)
        response = self.client.get(url_for('teams.teams_view'))
        self.assertEqual(api.teams.get.call_count, 1)
        self.assertEqual(response.context['teams'], teams)

    def test_teams_500_on_api_error(self, api):
        api.teams.get.side_effect = ApiException("url", "method", Exception())
        self.client.get(url_for('teams.teams_view'), expect_errors=True)

    def test_team_view_calls_api(self, api):
        team = TeamFactory()
        count = team.members_count
        memberships = [TeamMembershipFactory() for _ in xrange(count)]
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
