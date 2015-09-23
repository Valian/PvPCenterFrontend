# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask
from flask_babel import gettext
import flask_login

from api.models import Game
from common.utils import hash_by
from flask_frontend.common.view_helpers.contexts import IndexView
from flask_frontend.common.view_helpers.response_processors import TemplateRenderer, TemplateView, template_view
from flask_frontend.common.view_helpers.routes import UrlRoute, UrlRoutes
from flask_frontend.blueprints.games.forms import GameUpdateForm, GameJoinForm
from flask_frontend.common.flash import Flash
from flask_frontend.common.api_helper import get_or_404, get_or_none


def create_routes():
    return UrlRoutes([
        UrlRoute('/', IndexView(Game, TemplateRenderer('games.html'))),
        UrlRoute('/<int:game_id>/', TemplateView('game.html', create_edit_context), endpoint='game_view'),
        UrlRoute('/<int:game_id>/join', join, methods=['POST']),
        UrlRoute('/<int:game_id>/leave', leave, methods=['POST'])
    ])


def init_blueprint(blueprint, env):
    @blueprint.before_app_request
    def before_request():
        if 'static' not in flask.request.url:
            flask.g.games = get_or_none(env.api.games.get) or []


def create_edit_context(env, game_id):
    user = flask_login.current_user
    game = get_or_404(env.api.games.get_single, game_id=game_id)
    game_ownership = None
    form = None
    if user.is_authenticated():
        game_ownerships_by_game_id = hash_by(lambda go: go.game.id, user.game_ownerships)
        game_ownership = game_ownerships_by_game_id.get(game_id)
        if game_ownership:
            form = GameUpdateForm(env.api, user.token, game_ownership.id)
        else:
            form = GameJoinForm(env.api, user.token, game_id, user.id)
    return dict(game_ownership=game_ownership, form=form, game=game)


@template_view('game.html', create_edit_context)
@flask_login.login_required
def join(form):
    if form.validate_on_submit():
        Flash.success(gettext('Successfully updated!'))
        return dict(game_ownership=form.result)


@template_view('game.html', create_edit_context)
@flask_login.login_required
def leave(env, game_ownership):
    if game_ownership:
        delete = get_or_none(
            env.api.game_ownerships.delete, token=flask_login.current_user.token, game_ownership_id=game_ownership.id)
        if delete and delete.success:
            Flash.success("Successfully leaved game")
    else:
        Flash.error("Unable to leave game")
