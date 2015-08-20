# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask
import flask_wtf
from abc import abstractmethod
from flask.ext.babel import gettext

from common.logable import Logable
import flask_frontend.config.keys as conf_const
from api.api import PvPCenterApi, ApiException
from flask_frontend.common.utils import ConfigBlueprint


def get_api_instance(config):
    if not config[conf_const.MOCK_API]:
        from api.api import ApiDispatcher
        disp = ApiDispatcher(config[conf_const.BACKEND_URL])
    else:
        from api.mock import ApiDispatcherMock
        disp = ApiDispatcherMock(config[conf_const.BACKEND_URL])
    return PvPCenterApi(disp, config[conf_const.BACKEND_LOGIN], config[conf_const.BACKEND_PASS])


def get_or_none(func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        return result.data
    except ApiException:
        return None


def get_or_404(func, *args, **kwargs):
    result = get_or_none(func, *args, **kwargs)
    if result is None:
        flask.abort(404)
    return result


def get_or_500(func, *args, **kwargs):
    result = get_or_none(func, *args, **kwargs)
    if result is None:
        flask.abort(500)
    return result


class ApiBlueprint(ConfigBlueprint, Logable):
    """:type api: PvPCenterApi"""

    def __init__(self, name, import_name, config_keys=None, *args, **kwargs):
        """
        :type config_keys: list
        """
        super(ApiBlueprint, self).__init__(name, import_name, config_keys, *args, **kwargs)

        self.api = None

    def register(self, app, options, first_registration=False):
        super(ApiBlueprint, self).register(app, options, first_registration)
        self.api = get_api_instance(app.config)


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

