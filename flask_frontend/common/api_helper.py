# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask
import flask_login
import flask_wtf
from abc import abstractmethod
from flask_babel import gettext
from api.resource_endpoint import TokenParams
from common.logable import Logable

import flask_frontend.config.keys as conf_const
from api.resources import PvPCenterApi
from api.core import ApiException, ApiDispatcher


def get_api_instance(config):
    """
    :rtype: resources.api.PvPCenterApi
    """
    if config[conf_const.MOCK_API] or config[conf_const.TESTING]:
        from api.mock import ApiDispatcherMock
        disp = ApiDispatcherMock(config[conf_const.BACKEND_URL])
    else:
        from api.core import ApiDispatcher
        disp = ApiDispatcher(config[conf_const.BACKEND_URL])
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


class AutoParams(Logable):

    def __init__(self, method, allowed_params=None):
        """
        :type method: api.resource_endpoint.ResourceEndpoint
        :type allowed_params: list[str]
        """
        self.method = method
        self.allowed_params = allowed_params or method.params.get_available()

    def perform_request(self, **params):
        found_params = {}
        for param in self.allowed_params:
            if param == 'token':
                self._add_token(found_params)
            else:
                self._add_from_request_args(param, found_params)
        found_params.update(params)
        return self.method(**found_params)

    @staticmethod
    def _add_from_request_args(name, params):
        param = flask.request.args.get(name)
        if flask.request.method == 'POST':
            param = flask.request.form.get(name, param)
        if param is not None:
            params[name] = param

    @staticmethod
    def _add_token(params):
        user = flask_login.current_user
        if user.is_authenticated():
            params['token'] = user.token


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
        except Exception as e:
            self.server_errors = [gettext("Server error, try again later")]
            return False

    def _additional_validation(self):
        return True

    def _handle_errors(self, errors):
        for name, errors in errors.errors.items():
            if hasattr(self, name):
                attr = getattr(self, name)
                attr.errors.extend(errors)
            else:
                self.server_errors.extend(errors)

    @abstractmethod
    def _make_request(self):
        raise NotImplementedError()

