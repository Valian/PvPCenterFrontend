# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask
import flask_login
from flask_babel import gettext

import flask_frontend.blueprints.teams.helpers
from api.models import Team, TeamMembership
from flask.ext.frontend.blueprints.teams.menu import TeamMenu
from flask_frontend.common.utils import first_or_none
from flask_frontend.common.view_helpers.contexts import ApiResourceGet, ApiResourceIndex
from flask_frontend.common.view_helpers.response_processors import pjax_view, template_view, PjaxView
from flask_frontend.common.view_helpers.routes import UrlRoute, UrlRoutes
from flask_frontend.blueprints.teams.forms import CreateTeamForm, ChangeTeamLogoForm, EditTeamInfoForm
from flask_frontend.common.flash import Flash
from flask_frontend.common.api_helper import get_or_500, get_or_404


def create_routes():
    menu = TeamMenu()
    team_view = PjaxView('team_profile.html', ApiResourceGet(Team, allow_all_params=True))
    teams_view = PjaxView('teams_list.html', ApiResourceIndex(Team, allow_all_params=True))
    team_members = PjaxView('team_members.html', [ApiResourceGet(Team), ApiResourceIndex(TeamMembership, allow_all_params=True, out_name='memberships')])
    return UrlRoutes([
        UrlRoute('/', teams_view, endpoint="teams_view"),
        UrlRoute('/create', create_team_view, restrict=['logged_in'], methods=['GET', 'POST']),
        UrlRoute('/<int:team_id>', team_view, menu=menu, endpoint="team_view"),
        UrlRoute('/<int:team_id>/edit', edit, menu=menu, restrict=['team_owner']),
        UrlRoute('/<int:team_id>/change_basic', change_basic, menu=menu, restrict=['team_owner'], methods=['POST']),
        UrlRoute('/<int:team_id>/upload_logo', upload_logo, menu=menu, restrict=['team_owner'], methods=['POST']),
        UrlRoute('/<int:team_id>/members', team_members, endpoint='members_view', menu=menu),
        UrlRoute('/<int:team_id>/members/<int:user_id>/remove', remove_from_team, restrict=['team_owner'], methods=['POST'])
    ])

def create_edit_context(env, team_id):
    user = flask_login.current_user
    team = get_or_404(env.api.teams.get_single, team_id=team_id)
    change_logo_form = ChangeTeamLogoForm(team.id, user.token, env.api)
    change_basic_form = EditTeamInfoForm(user, team, env.api)
    return dict(team=team, logo_form=change_logo_form, basic_form=change_basic_form)


@pjax_view('team_edit.html', create_edit_context)
def edit(team, basic_form):
    basic_form.set_data(team)


@template_view('team_edit.html', create_edit_context)
def change_basic(basic_form):
    if basic_form.validate_on_submit():
        Flash.success(gettext("Team updated"))


@template_view('team_edit.html', create_edit_context)
def upload_logo(logo_form):
    if logo_form.validate_on_submit():
        Flash.success(gettext("Logo updated"))


@pjax_view('team_create.html')
def create_team_view(env):
    form = CreateTeamForm(flask_login.current_user, env.api)
    if form.validate_on_submit():
        Flash.success(gettext("Succesfully created team!"))
        return flask.redirect(flask.url_for('teams.team_view', team_id=form.result.id))
    return dict(form=form)

def remove_team_member_context(env, team_id, user_id):
    team = get_or_404(env.api.teams.get_single, team_id=team_id)
    membership = first_or_none(get_or_500(env.api.team_memberships.get, team_id=team.id, user_id=user_id))
    return dict(team=team, membership=membership)


@pjax_view('team_members.html', remove_team_member_context)
def remove_from_team(env, membership, team):
    if membership:
        response = env.api.team_memberships.delete(team_membership_id=membership.id, token=flask_login.current_user.token)
        if response.ok:
            Flash.success(gettext("Removed %(name)s from %(team)s", name=membership.user.name, team=membership.team.name))
            return flask.redirect(flask.url_for('teams.members_view', team_id=team.id))

    Flash.warning(gettext("Unable to remove user from team."))
    return flask.redirect(flask.url_for('teams.members_view', team_id=team.id))