# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
from functools import wraps
import flask

import flask_login
from flask.ext.frontend.blueprints.teams.forms import ChangeTeamLogoForm, EditTeamInfoForm
from flask.ext.frontend.common.api_helper import get_or_404
from flask.ext.frontend.common.utils import CustomRoute


def only_team_owner(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        logged_user = flask_login.current_user
        try:
            user_id = kwargs['team'].founder.id
            if not logged_user.is_authenticated() or logged_user.id != user_id:
                flask.abort(403)
        except (KeyError, AttributeError):
            flask.abort(500)
        return f(*args, **kwargs)
    return wrapper


class TeamRoute(CustomRoute):

    def prepare_view(self, team_id):
        team = get_or_404(self.blueprint.api.teams.get_single, team_id=team_id)
        return dict(team=team)


class TeamEditRoute(CustomRoute):

    def prepare_view(self, team_id):
        user = flask_login.current_user
        team = get_or_404(self.blueprint.api.teams.get_single, team_id=team_id)
        change_logo_form = ChangeTeamLogoForm(team.id, user.token, self.blueprint.api)
        change_basic_form = EditTeamInfoForm(user, team, self.blueprint.api)
        return dict(team=team, logo_form=change_logo_form, basic_form=change_basic_form)
