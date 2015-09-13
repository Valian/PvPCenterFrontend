# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
from functools import wraps

import flask
from flask.ext.babel import gettext
import flask_login

from . import games_blueprint
from common.utils import hash_by
from flask_frontend.blueprints.games.forms import GameUpdateForm, GameJoinForm
from flask_frontend.common.flash import Flash
from flask_frontend.common.utils import render_pjax, CustomRoute
from flask_frontend.common.api_helper import get_or_404, get_or_none


class GameRoute(CustomRoute):

    def prepare_view(self, game_id):
        user = flask_login.current_user
        game = get_or_404(games_blueprint.api.games.get_single, game_id)
        game_ownership = None
        form = None
        if user.is_authenticated():
            game_ownerships_by_game_id = hash_by(lambda go: go.game.id, user.game_ownerships)
            game_ownership = game_ownerships_by_game_id.get(game.id)
            if game_ownership:
                form = GameUpdateForm(games_blueprint.api, user.token, game_ownership.id)
            else:
                form = GameJoinForm(games_blueprint.api, user.token, game_id, user.id)

        return dict(game_ownership=game_ownership, form=form, game=game)

game_route = GameRoute(games_blueprint, '/<int:game_id>')


@games_blueprint.before_app_request
def before_request():
    if 'static' not in flask.request.url:
        flask.g.games = get_or_none(games_blueprint.api.games.get) or []


@games_blueprint.route('')
def games_view():
    return flask.render_template('games.html')


@game_route('')
def game_view(game, game_ownership, form):
    return flask.render_template('game.html', game=game, form=form, game_ownership=game_ownership)


@game_route('/join', methods=["POST"])
@flask_login.login_required
def join_game(game, game_ownership, form):
    if form.validate_on_submit():
        Flash.success(gettext('Successfully updated!'))
        game_ownership = form.result

    return render_pjax('game.html', 'game.html', game=game, form=form, game_ownership=game_ownership)


@game_route('/leave', methods=["POST"])
@flask_login.login_required
def leave_game(game, game_ownership, form):
    if game_ownership:
        delete = get_or_none(games_blueprint.api.game_ownerships.delete, flask_login.current_user.token, game_ownership.id)
        if delete and delete.success:
            Flash.success("Successfully leaved game")
            return render_pjax('game.html', 'game.html', game=game, form=form, game_ownership=game_ownership)

    Flash.success("Unable to leave game")
    return render_pjax('game.html', 'game.html', game=game, form=form, game_ownership=game_ownership)
