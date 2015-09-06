# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask
from flask.ext.babel import gettext
import flask_login
from flask.ext.frontend.blueprints.teams.forms import CreateTeamForm
from flask.ext.frontend.common.flash import Flash

from flask_frontend.common.api_helper import get_or_500
from flask_frontend.blueprints.teams import teams_blueprint


@teams_blueprint.route('')
def teams_view():
    teams = get_or_500(teams_blueprint.api.teams.get)
    return flask.render_template('teams.html', teams=teams)

@teams_blueprint.route('/create', methods=['POST', 'GET'])
@flask_login.login_required
def create_team_view():
    form = CreateTeamForm(flask_login.current_user.token, teams_blueprint.api)
    if form.validate_on_submit():
        Flash.success(gettext("Succesfully created team!"))
        return flask.redirect(flask.url_for('teams.team_view', team_id=form.result.id))

    return flask.render_template('team_create.html', form=form)

@teams_blueprint.route('/<int:team_id>')
def team_view(team_id):
    team = get_or_500(teams_blueprint.api.teams.get_single, team_id=team_id)
    team_memberships = get_or_500(teams_blueprint.api.team_memberships.get, team_id=team_id)
    members = map(lambda x: x.user, team_memberships)
    return flask.render_template('team.html', team=team, members=members)
