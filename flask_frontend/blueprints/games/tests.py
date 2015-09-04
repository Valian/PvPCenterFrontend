# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import mock
import flask
from api.api import ApiResult
from api.mock import create_mock_for
from api.models import ModelList, Game, UserGameOwnership

from flask_frontend.common.app_test_case import AppTestCase, logged_in


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

    @logged_in
    def test_join_game(self, user, mock_api):
        game = create_mock_for(Game)
        mock_api.games.get_single.return_value = ApiResult(data=game)
        user.game_ownerships = []
        self.client.post(flask.url_for('games.join_game', game_id=game.id), params={'nickname': 'testing'})
        self.assertTrue(mock_api.game_ownerships.create.called)
        self.assertFalse(mock_api.game_ownerships.update.called)

    @logged_in
    def test_update_game(self, user, mock_api):
        game = create_mock_for(Game)
        mock_api.games.get_single.return_value = ApiResult(data=game)
        user.game_ownerships = [create_mock_for(UserGameOwnership, game__id=game.id)]
        self.client.post(flask.url_for('games.join_game', game_id=game.id), params={'nickname': 'testing'})
        self.assertTrue(mock_api.game_ownerships.update.called)
        self.assertFalse(mock_api.game_ownerships.create.called)


