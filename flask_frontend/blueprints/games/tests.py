# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask
from api.mock import create_mock_for

from api.models import Game, UserGameOwnership

from flask_frontend.common.app_test_case import AppTestCase, logged_in, mock_api


class GamesTests(AppTestCase):

    @mock_api(Game, 'get')
    def test_get_games(self, get):
        response = self.client.get(flask.url_for('games.games_view'))
        self.assertTrue(get.called)
        self.assertEqual(response.status_code, 200)

    @mock_api(Game, 'get_single')
    def test_get_game(self, single):
        response = self.client.get(flask.url_for('games.game_view', game_id=1))
        self.assertTrue(single.called)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['game'], single.return_value.data)

    @mock_api(UserGameOwnership, 'create')
    @logged_in(game_ownerships=[])
    def test_join_game(self, create, user):
        self.client.post(flask.url_for('games.join', game_id=3), params={'nickname': 'testing'})
        self.assertTrue(create.called)

    @mock_api(UserGameOwnership, 'update')
    @logged_in(game_ownerships=[create_mock_for(UserGameOwnership, game__id=3)])
    def test_update_game(self, update, user):
        self.client.post(flask.url_for('games.join', game_id=3), params={'nickname': 'testing'})
        self.assertTrue(update.called)


