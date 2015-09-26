# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
from flask.ext.frontend.common.view_helpers.side_menu import SideMenuContext, SideMenu


class TeamMenu(SideMenuContext):

    def init_menu(self, menu):
        """
        :type menu: SideMenu
        """
        