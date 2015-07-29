# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask

from . import games_blueprint
from flask_frontend.common.api_helper import get_or_404, get_or_none


@games_blueprint.before_app_request
def before_request():
    flask.g.games = get_or_none(games_blueprint.api.games.get) or []


@games_blueprint.route('/games/<int:game_id>')
def game_view(game_id):
    game = get_or_404(games_blueprint.api.game.get, game_id)
    return flask.render_template('game.html', game=game)


@games_blueprint.route('/games')
def games_view():
    return flask.render_template('games.html')



