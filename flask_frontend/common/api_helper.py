# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import flask_wtf
import flask_frontend.config.keys as conf_const

from abc import ABCMeta, abstractmethod
from flask.ext.babel import gettext
from api.api import PvPCenterApi, ApiException
from flask_frontend.common.utils import ConfigBlueprint


class ApiBlueprint(ConfigBlueprint):
    """:type api: PvPCenterApi"""

    def __init__(self, name, import_name, config_keys=None, *args, **kwargs):
        """
        :type config_keys: list
        """
        config_keys = config_keys or []
        config_keys.extend([
            conf_const.BACKEND_URL, conf_const.BACKEND_LOGIN, conf_const.BACKEND_PASS, conf_const.MOCK_API])
        super(ApiBlueprint, self).__init__(name, import_name, config_keys, *args, **kwargs)

        self.api = None

    def register(self, app, options, first_registration=False):
        super(ApiBlueprint, self).register(app, options, first_registration)
        if not self.config[conf_const.MOCK_API]:
            from api.api import ApiDispatcher
            disp = ApiDispatcher(self.config[conf_const.BACKEND_URL])
        else:
            from api.mock import ApiDispatcherMock
            disp = ApiDispatcherMock(self.config[conf_const.BACKEND_URL])
        self.api = PvPCenterApi(disp, self.config[conf_const.BACKEND_LOGIN], self.config[conf_const.BACKEND_PASS])


class ApiForm(flask_wtf.Form):

    def __init__(self, api, *args, **kwargs):
        """
        :type api: PvPCenterApi
        """
        super(ApiForm, self).__init__(*args, **kwargs)
        self._api = api
        self.result = None
        self.server_errors = []

    def validate(self):
        rv = super(ApiForm, self).validate()
        if not rv:
            return False
        rv = self._additional_validation()
        if not rv:
            return False
        return self.validate_api_response()

    def validate_api_response(self):
        try:
            api_result = self._make_request()
            if api_result.ok:
                self.result = api_result.data
                return True
            self._handle_errors(api_result.errors)
            return False
        except ApiException as e:
            self.server_errors = [gettext("Server error, try again later")]
            return False

    def _additional_validation(self):
        return True

    @abstractmethod
    def _handle_errors(self, errors):
        raise NotImplementedError()

    @abstractmethod
    def _make_request(self):
        raise NotImplementedError()
