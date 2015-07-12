# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from api.api import ApiDispatcher, PvPCenterApi
from flask_frontend.common.utils import ConfigBlueprint
import flask_frontend.config.keys as conf_const


class ApiBlueprint(ConfigBlueprint):
    """:type api: PvPCenterApi"""

    def __init__(self, name, import_name, config_keys=None, *args, **kwargs):
        """
        :type config_keys: list
        """
        config_keys = config_keys or []
        config_keys.extend([conf_const.BACKEND_URL, conf_const.BACKEND_LOGIN, conf_const.BACKEND_PASS])
        super(ApiBlueprint, self).__init__(name, import_name, config_keys, *args, **kwargs)

        self.api = None

    def register(self, app, options, first_registration=False):
        super(ApiBlueprint, self).register(app, options, first_registration)
        disp = ApiDispatcher(self.config[conf_const.BACKEND_URL])
        self.api = PvPCenterApi(disp, self.config[conf_const.BACKEND_URL], self.config[conf_const.BACKEND_URL])
