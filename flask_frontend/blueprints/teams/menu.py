# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask.ext.babel import gettext
from flask.ext.frontend.common.view_helpers.side_menu import SideMenuContext, SideMenu, UrlConstructor


class TeamMenu(SideMenuContext):

    def init_menu(self, menu):
        """
        :type menu: SideMenu
        """
        team_url = UrlConstructor('teams.team_view', 'team_id')
        members_url = UrlConstructor('teams.members_view', 'team_id')
        settings_url = UrlConstructor('teams.edit', 'team_id')
        menu.add_entry(team_url, gettext('Profile'))
        menu.add_entry(members_url, gettext('Members'))
        menu.add_entry(team_url, gettext('Divisions'), 'team_member')
        menu.add_entry(team_url, gettext('Matches'), 'team_member')
        menu.add_entry(team_url, gettext('Challenges'), 'team_member')
        menu.add_entry(settings_url, gettext('Settings'), 'team_owner')
