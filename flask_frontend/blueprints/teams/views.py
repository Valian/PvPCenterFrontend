# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask
import flask_login
from flask_babel import gettext
from api.constants import TEAM_PROPOSITION_TYPE
from flask.ext.frontend.common.view_helpers.core import view
from flask.ext.frontend.common.views.core import ApiResourceGetMixin, ApiResourceIndexMixin, PjaxRendererMixin, \
    TemplateRendererMixin, RestrictionMixin
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
from flask_frontend.common.api_helper import get_or_500, get_or_404, AutoParams


def create_routes():
    menu = TeamMenu()

    return UrlRoutes([
        UrlRoute('/', TeamsView),
        UrlRoute('/create', TeamCreateView),
        UrlRoute('/propose', TeamProposeUserView),
        UrlRoute('/accept_invite', TeamAcceptPropositionView),
        UrlRoute('/decline_proposition', TeamDeclinePropositionView),
        UrlRoute('/remove_from_team', TeamRemoveMemberView),
        UrlRoute('/<int:team_id>', TeamView),
        UrlRoute('/<int:team_id>/edit', TeamEditView),
        UrlRoute('/<int:team_id>/change_basic', TeamChangeBasicView),
        UrlRoute('/<int:team_id>/upload_logo', TeamChangeLogoView),
        UrlRoute('/<int:team_id>/members', TeamMembersView)
    ])


class TeamView(ApiResourceGetMixin, PjaxRendererMixin, View):

    model = Team
    template = 'team_profile.html'
    endpoint = 'teams.team_view'


class TeamsView(ApiResourceIndexMixin, PjaxRendererMixin, View):

    model = Team
    template = 'teams_list.html'
    endpoint = 'teams.teams_view'


class TeamMembersView(TeamView):

    endpoint = 'teams.members_view'
    template = 'team_members.html'

    def process_params(self, **kwargs):
        kwargs = super(TeamMembersView, self).process_params(**kwargs)
        auto_params = AutoParams(self.env.api.team_memberships.get)
        kwargs['memberships'] = get_or_500(auto_params.perform_request(**kwargs))
        return kwargs


class BaseEditView(RestrictionMixin, PjaxRendererMixin, View):

    template = 'team_edit.html'
    restrictions = ['team_owner']

    def process_params(self, team_id, **kwargs):
        user = flask_login.current_user
        team = get_or_404(self.env.api.teams.get_single, team_id=team_id)
        change_logo_form = ChangeTeamLogoForm(team.id, user.token, self.env.api)
        change_basic_form = EditTeamInfoForm(user, team, self.env.api)
        kwargs.update(dict(team=team, logo_form=change_logo_form, basic_form=change_basic_form))
        return kwargs


class TeamEditView(BaseEditView):

    endpoint = 'teams.edit'

    def view_func(self, team, basic_form, **kwargs):
        basic_form.set_data(team)


class TeamChangeBasicView(BaseEditView):

    endpoint = 'teams.change_basic'
    methods = ['POST']

    def view_func(self, basic_form, **kwargs):
        if basic_form.validate_on_submit():
            Flash.success(gettext("Team updated"))


class TeamChangeLogoView(BaseEditView):

    endpoint = 'teams.upload_logo'
    methods = ['POST']

    def view_func(self, logo_form, **kwargs):
        if logo_form.validate_on_submit():
            Flash.success(gettext("Logo updated"))


class TeamProposeUserView(RestrictionMixin, View):

    restrictions = ['logged_in']
    endpoint = 'teams.propose_user'
    methods = ['POST']

    def process_params(self, **kwargs):
        team_id = int(flask.request.form.get('team_id'))
        user_id = int(flask.request.form.get('user_id'))
        type = flask.request.form.get('type')
        if team_id is None or user_id is None or type is None:
            flask.abort(401)
        kwargs.update(dict(team_id=team_id, user_id=user_id, type=type))
        return kwargs

    def view_func(self, team_id, user_id, type, **kwargs):
        # TODO - return to referrer
        token = flask_login.current_user.token
        response = self.env.api.team_propositions.create(token=token, team_id=team_id, user_id=user_id, type=type)
        if response.ok:
            if type == TEAM_PROPOSITION_TYPE.INVITE:
                Flash.success(gettext("Successfully invited user to team!"))
            else:
                Flash.success(gettext("Request sent!"))
        else:
            Flash.error("Unable to proceed!")
        return flask.redirect(flask.url_for('teams.team_view', team_id=team_id))


class TeamPropositionBaseView(RestrictionMixin, View):

    restrictions = ['logged_in']

    def view_func(self, team_proposition, **kwargs):
        # TODO - redirect to referer
        response = self.make_request(team_proposition)
        if response.ok:
            Flash.success(gettext("Operation successfull!"))
        else:
            Flash.error(gettext("Unable to perform operation"))
        return flask.redirect(flask.url_for('teams.teams_view'))

    def process_params(self, **kwargs):
        team_id = int(flask.request.form.get('team_id'))
        user_id = int(flask.request.form.get('user_id'))
        if team_id is None or user_id is None:
            flask.abort(401)
        team_proposition = first_or_none(get_or_500(
            self.env.api.team_propositions.get, token=flask_login.current_user.token, team_id=team_id, user_id=user_id))
        kwargs.update(dict(team_proposition=team_proposition))
        return kwargs

    def make_request(self, team_proposition):
        raise NotImplementedError()


class TeamAcceptPropositionView(TeamPropositionBaseView):

    endpoint = 'teams.accept_proposition'
    methods = ['POST']

    def make_request(self, team_proposition):
        token = flask_login.current_user.token
        return self.env.api.team_propositions.accept(token=token, team_proposition_id=team_proposition.id)


class TeamDeclinePropositionView(TeamPropositionBaseView):

    endpoint = 'teams.accept_proposition'
    methods = ['POST']

    def make_request(self, team_proposition):
        token = flask_login.current_user.token
        return self.env.api.team_propositions.delete(token=token, team_proposition_id=team_proposition.id)


class TeamCreateView(PjaxRendererMixin, RestrictionMixin, View):

    template = 'team_create.html'
    endpoint = 'teams.create_team_view'
    methods = ['GET', 'POST']
    restrictions = ['logged_in']

    def view_func(self, **kwargs):
        form = CreateTeamForm(flask_login.current_user, self.env.api)
        if form.validate_on_submit():
            Flash.success(gettext("Succesfully created team!"))
            return flask.redirect(flask.url_for('teams.team_view', team_id=form.result.id))
        return dict(form=form)


class TeamRemoveMemberView(RestrictionMixin, PjaxRendererMixin, View):

    endpoint = 'teams.remove_from_team'
    template = 'team_members.html'
    methods = ['POST']
    restrictions = ['logged_in']

    def process_params(self, **kwargs):
        team_id = int(flask.request.form.get('team_id'))
        user_id = int(flask.request.form.get('user_id'))
        if team_id is None or user_id is None:
            flask.abort(401)
        team = get_or_404(self.env.api.teams.get_single, team_id=team_id)
        membership = first_or_none(get_or_500(self.env.api.team_memberships.get, team_id=team.id, user_id=user_id))
        kwargs.update(dict(team=team, membership=membership))
        return kwargs

    def view_func(self, membership, team, **kwargs):
        if membership:
            response = self.env.api.team_memberships.delete(team_membership_id=membership.id, token=flask_login.current_user.token)
            if response.ok:
                Flash.success(
                    gettext("Removed %(name)s from %(team)s", name=membership.user.name, team=membership.team.name))
                return flask.redirect(flask.url_for('teams.members_view', team_id=team.id))

        Flash.warning(gettext("Unable to remove user from team."))
        return flask.redirect(flask.url_for('teams.members_view', team_id=team.id))
