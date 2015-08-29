# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import mock
import flask
from api.api import ApiResult
from api.mock import create_mock_for
from api.models import ModelList, Game

from flask_frontend.common.app_test_case import AppTestCase


@mock.patch('flask_frontend.blueprints.games.views.games_blueprint.api')
class GamesTests(AppTestCase):

    def test_get_games(self, mock_api):
        count = 5
        mock_api.games.get.return_value = ApiResult(data=create_mock_for(ModelList.For(Game), list_count=count))
        response = self.client.get(flask.url_for('games.games_view'))
        self.assertTrue(mock_api.games.get.called)
        self.assertEqual(response.status_code, 200)

    def test_get_game(self, mock_api):
        game = create_mock_for(Game)
        mock_api.games.get_single.return_value = ApiResult(data=game)
        response = self.client.get(flask.url_for('games.game_view', game_id=1))
        self.assertTrue(mock_api.games.get_single.called)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['game'], game)
