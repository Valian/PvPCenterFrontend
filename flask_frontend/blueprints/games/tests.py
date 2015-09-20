# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import mock
import flask
from api.api import ApiResult
from api.mock import create_mock_for
from api.models import ModelList, Game, UserGameOwnership

from flask_frontend.common.app_test_case import AppTestCase, logged_in


class GamesTests(AppTestCase):

    def test_get_games(self, m_games__get):
        response = self.client.get(flask.url_for('games.games_view'))
        self.assertTrue(m_games__get.called)
        self.assertEqual(response.status_code, 200)

    def test_get_game(self, m_games__get_single):
        response = self.client.get(flask.url_for('games.game_view', game_id=1))
        self.assertTrue(m_games__get_single.called)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['game'], m_games__get_single.return_value.data)

    @logged_in
    def test_join_game(self, user, m_game_ownerships__create, m_games__get_single):
        game = m_games__get_single.return_value.data
        user.game_ownerships = []
        self.client.post(flask.url_for('games.join', game_id=game.id), params={'nickname': 'testing'})
        self.assertTrue(m_game_ownerships__create.called)

    @logged_in
    def test_update_game(self, user, m_game_ownerships__update, m_games__get_single):
        game = m_games__get_single.return_value.data
        self.client.post(flask.url_for('games.join', game_id=game.id), params={'nickname': 'testing'})
        self.assertTrue(m_game_ownerships__update.called)


