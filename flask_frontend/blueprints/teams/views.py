# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask

from flask_frontend.common.api_helper import get_or_500
from flask_frontend.blueprints.teams import teams_blueprint


@teams_blueprint.route('')
def teams_view():
    teams = get_or_500(teams_blueprint.api.teams.get)
    return flask.render_template('teams.html', teams=teams)


@teams_blueprint.route('/<int:team_id>')
def team_view(team_id):
    team = get_or_500(teams_blueprint.api.team.get, team_id=team_id)
    team_memberships = get_or_500(teams_blueprint.api.team_memberships.get, team_id=team_id)
    members = map(lambda x: x.user, team_memberships)
    return flask.render_template('team.html', team=team, members=members)
