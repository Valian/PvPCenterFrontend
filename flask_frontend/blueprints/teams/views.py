# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask
from flask.ext.babel import gettext
import flask_login

from flask.ext.frontend.blueprints.teams.helpers import TeamRoute, only_team_owner
from flask.ext.frontend.common.views import route, TemplateView, register
from flask_frontend.blueprints.teams.forms import CreateTeamForm, ChangeTeamLogoForm, EditTeamInfoForm
from flask_frontend.common.flash import Flash
from flask_frontend.common.pagination import Pagination
from flask_frontend.common.utils import pjax
from flask_frontend.common.api_helper import get_or_500, get_or_404
from flask_frontend.blueprints.teams import teams_blueprint


team_route = TeamRoute(teams_blueprint, '/<int:team_id>')


@register(teams_blueprint)
class EditTeamViews(TemplateView):

    decorators = [only_team_owner]
    template = 'team_edit.html'

    @route('/<int:team_id>')
    def create_context(self, team_id):
        user = flask_login.current_user
        team = get_or_404(teams_blueprint.api.teams.get_single, team_id=team_id)
        change_logo_form = ChangeTeamLogoForm(team.id, user.token, teams_blueprint.api)
        change_basic_form = EditTeamInfoForm(user, team, teams_blueprint.api)
        return dict(team=team, logo_form=change_logo_form, basic_form=change_basic_form)

    def edit(self, team, basic_form):
        basic_form.set_data(team)

    @route(methods=['POST'])
    def change_basic(self, basic_form):
        if basic_form.validate_on_submit():
            Flash.success(gettext("Team updated"))

    @route(methods=['POST'])
    def upload_logo(self, logo_form):
        if logo_form.validate_on_submit():
            Flash.success(gettext("Logo updated"))


@teams_blueprint.route('')
def teams_view():
    name = flask.request.args.get('name', '')
    teams = get_or_500(teams_blueprint.api.teams.get, name=name)
    pagination = Pagination.create_from_model_list(teams)
    return pjax('teams_list.html', teams=teams, pagination=pagination)


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
    return pjax('team_profile.html', team=team)


@team_route('/members')
def members_view(team):
    team_memberships = get_or_500(teams_blueprint.api.team_memberships.get, team_id=team.id)
    pagination = Pagination.create_from_model_list(team_memberships)
    return pjax('team_members.html', team=team, memberships=team_memberships, pagination=pagination)


@team_route('/remove', methods=['POST'])
def remove_from_team(team):
    # TODO
    team_memberships = get_or_500(teams_blueprint.api.team_memberships.get, team_id=team.id)
    pagination = Pagination.create_from_model_list(team_memberships)
    return pjax('team_members.html', team=team, memberships=team_memberships, pagination=pagination)
