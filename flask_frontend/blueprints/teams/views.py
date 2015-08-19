# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask

from flask_frontend.common.api_helper import get_or_none
from flask_frontend.blueprints.teams import teams_blueprint


@teams_blueprint.route('')
def teams_view():
    teams = get_or_none(teams_blueprint.api.teams.get)
    return flask.render_template('teams.html', teams=teams)
