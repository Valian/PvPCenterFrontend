# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import urlparse
from abc import ABCMeta, abstractmethod
import requests
from api.models import Errors
from common.logable import Logable


class ApiException(Exception):

    def __init__(self, url, method, e):
        super(ApiException, self).__init__('error while performing {0} {1}, more info: {2}'.format(url, method, e))
        self.url = url
        self.method = method


class ApiResult(object):

    def __init__(self, data=None, errors=None, status=200):
        self.status = status
        self.errors = errors
        self.data = data
        self.ok = not self.errors or len(errors) == 0


class ApiDispatcherBase(Logable):

    __metaclass__ = ABCMeta

    def __init__(self, base_url, additional_params=None):
        self.base_url = base_url
        self.additional_params = additional_params or {}

    def add_additional_params(self, **kwargs):
        self.additional_params.update(kwargs)

    @abstractmethod
    def make_request(self, method, endpoint, model, **kwargs):
        raise NotImplementedError


class ApiDispatcher(ApiDispatcherBase):

    def make_request(self, method, endpoint, model, **kwargs):
        try:
            url = self.create_url(endpoint)
            params = dict(self.additional_params)
            params.update(kwargs)
            self.log_debug("Performing {0} request to {1}. Additional: {2}".format(method, url, str(kwargs)))
            response = self._send_request(method, url, **params)
            self.log_debug("Performed {0} {1}, response code: {2}".format(url, method, response.status_code))
            return self._convert_to_api_result(model, response)
        except Exception as e:
            self.log_error("Error while performing request, more info: {0}".format(e))
            raise ApiException(endpoint, method, e)

    def create_url(self, endpoint):
        return urlparse.urljoin(self.base_url, endpoint)

    @staticmethod
    def _send_request(method, url, **kwargs):
        method = getattr(requests, method.lower())
        return method(url, **kwargs)

    def _convert_to_api_result(self, model, response):
        json = response.json()
        self.log_debug('Response data: {0}'.format(json))
        if not response.ok:
            return ApiResult(errors=Errors.from_json(json), status=response.status_code)
        else:
            return ApiResult(data=model.from_json(json) if model else json, status=response.status_code)