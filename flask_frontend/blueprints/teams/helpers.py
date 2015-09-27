# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask
import flask_login

from flask.ext.frontend.common.utils import first_or_none
from flask.ext.frontend.common.view_helpers.restrictions import RestrictionRegistry
from flask_frontend.common.api_helper import get_or_404, get_or_500


@RestrictionRegistry.register('team_owner')
def only_team_owner(env, kwargs):
    logged_user = flask_login.current_user
    if 'team' in kwargs:
        user_id = kwargs['team'].founder.id
    elif 'team_id' in flask.request.view_args:
        team = get_or_404(env.api.teams.get_single, team_id=flask.request.view_args['team_id'])
        user_id = team.founder.id
    else:
        raise EnvironmentError('No team or team_id in view params')
    return logged_user.is_authenticated() and logged_user.id == user_id


@RestrictionRegistry.register('team_member')
def only_team_member(env, kwargs):
    logged_user = flask_login.current_user
    if not logged_user.is_authenticated():
        return False
    if 'team' in kwargs:
        team_id = kwargs['team'].id
    elif 'team_id' in flask.request.view_args:
        team_id = kwargs['team_id']
    else:
        raise EnvironmentError('No team or team_id in view params')
    membership = first_or_none(get_or_500(env.api.team_memberships.get, team_id=team_id, user_id=logged_user.id))
    return membership is not None
