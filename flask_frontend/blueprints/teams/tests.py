# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask import url_for
import mock

from api.api import ApiResult
from api.mock import TeamFactory
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
