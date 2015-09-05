# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask
from flask.ext.babel import gettext
import flask_login

from . import games_blueprint
from common.utils import hash_by
from flask.ext.frontend.blueprints.games.forms import GameUpdateForm, GameJoinForm
from flask.ext.frontend.common.flash import Flash
from flask.ext.frontend.common.utils import render_pjax
from flask_frontend.common.api_helper import get_or_404, get_or_none


@games_blueprint.before_app_request
def before_request():
    flask.g.games = get_or_none(games_blueprint.api.games.get) or []


@games_blueprint.route('')
def games_view():
    return flask.render_template('games.html')


@games_blueprint.route('/<int:game_id>')
def game_view(game_id):
    game = get_or_404(games_blueprint.api.games.get_single, game_id)
    form, type = None, None
    if flask_login.current_user.is_authenticated():
        form, type = get_game_ownership_form(game_id, flask_login.current_user)
    return flask.render_template('game.html', game=game, form=form, type=type)

@games_blueprint.route('/<int:game_id>/join', methods=["POST"])
@flask_login.login_required
def join_game(game_id):
    game = get_or_404(games_blueprint.api.games.get_single, game_id)
    user = flask_login.current_user
    form, type = get_game_ownership_form(game_id, user)

    if form.validate_on_submit():
        Flash.success(gettext('Successfully updated!'))
        return flask.redirect(flask.url_for('games.game_view', game_id=game_id))

    return render_pjax('game.html', 'game.html', game=game, form=form, type=type)


def get_game_ownership_form(game_id, user):
    game_ownerships_by_game_id = hash_by(lambda go: go.game.id, user.game_ownerships)
    if game_id in game_ownerships_by_game_id:
        game_own = game_ownerships_by_game_id[game_id]
        form = GameUpdateForm(games_blueprint.api, user.token, game_own.id)
        type = 'update'
    else:
        form = GameJoinForm(games_blueprint.api, user.token, game_id, user.id)
        type = 'create'
    return form, type
