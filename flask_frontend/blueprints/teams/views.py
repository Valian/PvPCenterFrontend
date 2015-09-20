# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask
import flask_login

from flask.ext.babel import gettext
from flask.ext.frontend.blueprints.teams.helpers import only_team_owner
from flask.ext.frontend.common.utils import restrict
from flask.ext.frontend.common.view import pjax_view, template_view, UrlRoute, UrlRoutes, PjaxView, ApiIndexMethod, \
    ApiGetMethod

from flask_frontend.blueprints.teams.forms import CreateTeamForm, ChangeTeamLogoForm, EditTeamInfoForm
from flask_frontend.common.flash import Flash
from flask_frontend.common.pagination import Pagination
from flask_frontend.common.api_helper import get_or_500, get_or_404


def create_routes(env):
    team_view = PjaxView('team_profile.html', ApiGetMethod('team', env.api.teams.get_single, allow_all_params=True))
    teams_view = PjaxView('teams_list.html', ApiIndexMethod('teams', env.api.teams.get, allow_all_params=True))
    return UrlRoutes([
        UrlRoute('/', teams_view, endpoint='teams_view'),
        UrlRoute('/create', create_team_view),
        UrlRoute('/<int:team_id>', team_view, endpoint='team_view'),
        UrlRoute('/<int:team_id>/edit', edit),
        UrlRoute('/<int:team_id>/change_basic', change_basic, methods=['POST']),
        UrlRoute('/<int:team_id>/upload_logo', upload_logo, methods=['POST']),
        UrlRoute('/<int:team_id>/members', members_view),
        UrlRoute('/<int:team_id>/members/<int:user_id>/remove', remove_from_team, methods=['POST'])
    ])


@flask_login.login_required
def create_edit_context(env, team_id):
    user = flask_login.current_user
    team = get_or_404(env.api.teams.get_single, team_id=team_id)
    change_logo_form = ChangeTeamLogoForm(team.id, user.token, env.api)
    change_basic_form = EditTeamInfoForm(user, team, env.api)
    return dict(team=team, logo_form=change_logo_form, basic_form=change_basic_form)


@pjax_view('team_edit.html', create_edit_context)
@restrict(only_team_owner)
def edit(team, basic_form):
    basic_form.set_data(team)


@template_view('team_edit.html', create_edit_context)
@restrict(only_team_owner)
def change_basic(basic_form):
    if basic_form.validate_on_submit():
        Flash.success(gettext("Team updated"))


@template_view('team_edit.html', create_edit_context)
@restrict(only_team_owner)
def upload_logo(logo_form):
        if logo_form.validate_on_submit():
            Flash.success(gettext("Logo updated"))


@pjax_view('team_create.html')
@flask_login.login_required
def create_team_view(env):
    form = CreateTeamForm(flask_login.current_user, env.api)
    if form.validate_on_submit():
        Flash.success(gettext("Succesfully created team!"))
        return flask.redirect(flask.url_for('teams.team_view', team_id=form.result.id))
    return dict(form=form)


def get_team_members_context(env, team_id):
    team = get_or_404(env.api.teams.get_single, team_id=team_id)
    team_memberships = get_or_500(env.api.team_memberships.get, team_id=team.id)
    pagination = Pagination.create_from_model_list(team_memberships)
    return dict(team=team, memberships=team_memberships, pagination=pagination)


@pjax_view('team_members.html', get_team_members_context)
def members_view():
    pass


@pjax_view('team_members.html', get_team_members_context)
def remove_from_team():
    pass
