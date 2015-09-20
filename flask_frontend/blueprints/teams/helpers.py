# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask

import flask_login
from flask.ext.frontend.blueprints.teams.forms import ChangeTeamLogoForm, EditTeamInfoForm
from flask.ext.frontend.common.api_helper import get_or_404
from flask.ext.frontend.common.utils import CustomRoute, RestrictionDecorator


def only_team_owner(*args, **kwargs):
    logged_user = flask_login.current_user
    if 'team' in kwargs:
        user_id = kwargs['team'].founder.id
    elif 'team_id' in flask.request.view_args:
        api = flask.current_app.api
        team = get_or_404(api.teams.get_single(flask.request.view_args['team_id']))
        user_id = team.founder.id
    else:
        raise EnvironmentError('No team or team_id in view params')
    if not logged_user.is_authenticated() or logged_user.id != user_id:
        flask.abort(403)


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
