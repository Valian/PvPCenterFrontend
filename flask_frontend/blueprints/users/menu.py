# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask_babel import gettext

from flask_frontend.common.view_helpers.side_menu import SideMenuContext, UrlConstructor, SideMenu


class UsersSideMenu(SideMenuContext):

    def init_menu(self, menu):
        """
        :type menu: SideMenu
        """
        profile_url = UrlConstructor('users.user_view', 'user_id')
        friends_url = UrlConstructor('users.friends_view', 'user_id')
        teams_url = UrlConstructor('users.teams_view', 'user_id')
        edit_url = UrlConstructor('users.edit_profile_view', 'user_id')
        return (
            menu.add_entry(profile_url, gettext('Profile')),
            menu.add_entry(friends_url, gettext('Friends'), 'current_user'),
            menu.add_entry(None, gettext('Messages'), 'current_user'),
            menu.add_entry(None, gettext('Matches')),
            menu.add_entry(None, gettext('Challenges')),
            menu.add_entry(None, gettext('Leagues')),
            menu.add_entry(edit_url, gettext('Settings'), 'current_user'),
            menu.add_entry(teams_url, gettext('Teams'))
        )
