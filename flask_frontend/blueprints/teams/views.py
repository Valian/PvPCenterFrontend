# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask
from flask.ext.babel import gettext
import flask_login
from flask.ext.frontend.blueprints.teams.helpers import TeamRoute, TeamEditRoute, only_team_owner
from flask_frontend.blueprints.teams.forms import CreateTeamForm
from flask_frontend.common.flash import Flash
from flask_frontend.common.pagination import Pagination
from flask_frontend.common.utils import render_pjax

from flask_frontend.common.api_helper import get_or_500
from flask_frontend.blueprints.teams import teams_blueprint


team_route = TeamRoute(teams_blueprint, '/<int:team_id>')
edit_route = TeamEditRoute(teams_blueprint, '/<int:team_id>')


@teams_blueprint.route('')
def teams_view():
    name = flask.request.args.get('name', '')
    teams = get_or_500(teams_blueprint.api.teams.get, name=name)
    pagination = Pagination.create_from_model_list(teams)
    return render_pjax('teams_list.html', 'teams_list_result.html', teams=teams, pagination=pagination)


@teams_blueprint.route('/create', methods=['POST', 'GET'])
@flask_login.login_required
def create_team_view():
    form = CreateTeamForm(flask_login.current_user, teams_blueprint.api)
    if form.validate_on_submit():
        Flash.success(gettext("Succesfully created team!"))
        return flask.redirect(flask.url_for('teams.team_view', team_id=form.result.id))

    return flask.render_template('team_create.html', form=form)


@team_route('')
def team_view(team):
    team_memberships = get_or_500(teams_blueprint.api.team_memberships.get, team_id=team.id)
    members = map(lambda x: x.user, team_memberships)
    return flask.render_template('team.html', team=team, members=members)


@edit_route('/edit')
@only_team_owner
def edit_team_view(team, logo_form, basic_form):
    basic_form.set_data(team)
    return flask.render_template('team_edit.html', team=team, logo_form=logo_form, basic_form=basic_form)


@edit_route('/change_basic', methods=['POST'])
@only_team_owner
def change_basic(team, logo_form, basic_form):
    if basic_form.validate_on_submit():
        Flash.success(gettext("Team updated"))
    return flask.render_template('team_edit.html', team=team, logo_form=logo_form, basic_form=basic_form)


@edit_route('/upload_logo', methods=['POST'])
@only_team_owner
def upload_logo(team, logo_form, basic_form):
    if logo_form.validate_on_submit():
        Flash.success(gettext("Logo updated"))
    return flask.render_template('team_edit.html', team=team, logo_form=logo_form, basic_form=basic_form)