# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask

from flask_frontend.common.app_test_case import AppTestCase


class GamesTests(AppTestCase):

    def test_get_games(self):
        response = self.client.get(flask.url_for('games.games_view'))

    def test_get_game(self):
        response = self.client.get(flask.url_for('games.game_view', game_id=1))