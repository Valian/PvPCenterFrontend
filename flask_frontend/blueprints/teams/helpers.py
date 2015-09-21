# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask
import flask_login

from flask_frontend.common.api_helper import get_or_404


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
