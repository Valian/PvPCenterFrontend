# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask
from flask.ext.babel import gettext
import flask_login

from common.utils import hash_by
from flask.ext.frontend.common.view import UrlRoutes, PjaxView
from flask_frontend.blueprints.games.forms import GameUpdateForm, GameJoinForm
from flask_frontend.common.flash import Flash
from flask_frontend.common.api_helper import get_or_404, get_or_none


def create_routes(env):
    games_view = PjaxView()
    return UrlRoutes([

    ])

def init_blueprint(blueprint, env):

    @blueprint.before_app_request
    def before_request():
        if 'static' not in flask.request.url:
            flask.g.games = get_or_none(env.api.games.get) or []


@games_blueprint.route('')
def games_view():
    return flask.render_template('games.html')

@register(games_blueprint)
class GameView(PjaxView):

    template = 'game.html'

    @route('/<int:game_id>/')
    def create_context(self, game_id):
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

    @route('')
    def show(self):
        pass

    @route(methods=["POST"])
    @flask_login.login_required
    def join(self, form):
        if form.validate_on_submit():
            Flash.success(gettext('Successfully updated!'))
            return dict(game_ownership=form.result)

    @route(methods=["POST"])
    @flask_login.login_required
    def leave(self, game_ownership):
        if game_ownership:
            delete = get_or_none(
                games_blueprint.api.game_ownerships.delete, flask_login.current_user.token, game_ownership.id)
            if delete and delete.success:
                Flash.success("Successfully leaved game")
        else:
            Flash.error("Unable to leave game")
