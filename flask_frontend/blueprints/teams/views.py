# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask
import flask_login
from flask_babel import gettext
from api.constants import TEAM_PROPOSITION_TYPE
from flask.ext.frontend.common.view_helpers.core import view
from flask.ext.frontend.common.views.core import ApiResourceGetMixin, ApiResourceIndexMixin
from flask.ext.frontend.common.views.core import View

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
        UrlRoute('/propose', propose_user, restrict=['logged_in'], methods=['POST']),
        UrlRoute('/accept_invite', accept_proposition, restrict=['logged_in'], methods=['POST']),
        UrlRoute('/decline_proposition', decline_proposition, restrict=['logged_in'], methods=['POST']),
        UrlRoute('/remove_from_team', remove_from_team, restrict=['logged_in'], methods=['POST']),
        UrlRoute('/<int:team_id>', team_view, menu=menu, endpoint="team_view"),
        UrlRoute('/<int:team_id>/edit', edit, menu=menu, restrict=['team_owner']),
        UrlRoute('/<int:team_id>/change_basic', change_basic, menu=menu, restrict=['team_owner'], methods=['POST']),
        UrlRoute('/<int:team_id>/upload_logo', upload_logo, menu=menu, restrict=['team_owner'], methods=['POST']),
        UrlRoute('/<int:team_id>/members', team_members, endpoint='members_view', menu=menu)
    ])


class TeamView(ApiResourceGetMixin, View):

    model = Team
    endpoint = 'teams.team_view'


class TeamsView(ApiResourceIndexMixin, View):

    model = Team
    endpoint = 'teams.teams_view'


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


def create_proposition_context_creator(env):
    team_id = int(flask.request.form.get('team_id'))
    user_id = int(flask.request.form.get('user_id'))
    type = flask.request.form.get('type')
    if team_id is None or user_id is None or type is None:
        flask.abort(401)
    return dict(team_id=team_id, user_id=user_id, type=type)


@view(context_creators=create_proposition_context_creator)
def propose_user(env, team_id, user_id, type):
    # TODO - return to referrer
    token = flask_login.current_user.token
    response = env.api.team_propositions.create(token=token, team_id=team_id, user_id=user_id, type=type)
    if response.ok:
        if type == TEAM_PROPOSITION_TYPE.INVITE:
            Flash.success(gettext("Successfully invited user to team!"))
        else:
            Flash.success(gettext("Request sent!"))
    else:
        Flash.error("Unable to proceed!")
    return flask.redirect(flask.url_for('teams.team_view', team_id=team_id))


def proposition_context_creator(env):
    team_id = int(flask.request.form.get('team_id'))
    user_id = int(flask.request.form.get('user_id'))
    if team_id is None or user_id is None:
        flask.abort(401)
    team_proposition = first_or_none(get_or_500(
        env.api.team_propositions.get, token=flask_login.current_user.token, team_id=team_id, user_id=user_id))
    return dict(team_proposition=team_proposition)


@view(context_creators=proposition_context_creator)
def accept_proposition(env, team_proposition):
    # TODO - redicrect to referer
    token = flask_login.current_user.token
    response = env.api.team_propositions.accept(token=token, team_proposition_id=team_proposition.id)
    if response.ok:
        Flash.success(gettext("Operation successfull!"))
    else:
        Flash.error(gettext("Unable to perform operation"))
    return flask.redirect(flask.url_for('teams.teams_view'))


@view(context_creators=proposition_context_creator)
def decline_proposition(env, team_proposition):
    # TODO - redicrect to referer
    token = flask_login.current_user.token
    response = env.api.team_propositions.delete(token=token, team_proposition_id=team_proposition.id)
    if response.ok:
        Flash.success(gettext("Operation successfull!"))
    else:
        Flash.error(gettext("Unable to perform operation"))
    return flask.redirect(flask.url_for('teams.teams_view'))


@pjax_view('team_create.html')
def create_team_view(env):
    form = CreateTeamForm(flask_login.current_user, env.api)
    if form.validate_on_submit():
        Flash.success(gettext("Succesfully created team!"))
        return flask.redirect(flask.url_for('teams.team_view', team_id=form.result.id))
    return dict(form=form)


def remove_team_member_context(env):
    team_id = int(flask.request.form.get('team_id'))
    user_id = int(flask.request.form.get('user_id'))
    if team_id is None or user_id is None:
        flask.abort(401)
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