# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import logging

import urllib

import re

from .models import ModelList, DeleteResponse
from common.logable import Logable
from flask_frontend.common.pagination import get_pagination_params


class Params(object):

    def __init__(self, *args, **kwargs):
        self._params = self._create_params(args, kwargs)

    @staticmethod
    def _create_params(args, kwargs):
        params = {}
        for name in args:
            params[name] = name
        for name, translation in kwargs.iteritems():
            params[name] = translation
        return params

    def add_param(self, name, translation=None):
        self._params[name] = translation

    def extract_and_translate(self, provided_params):
        return {self._params[name]: provided_params[name] for name in self._params if name in provided_params}

    def get_available(self):
        return set(self._params.values())

    def __contains__(self, item):
        return item in self._params

    def __add__(self, other):
        if not isinstance(other, Params):
            raise ValueError("Unable to add {0} to Params class".format(other))
        new_params = self._params.copy()
        new_params.update(other._params)
        return Params(**new_params)


class TokenParams(Params):

    def __init__(self, *args, **kwargs):
        super(TokenParams, self).__init__(*args, **kwargs)
        self.add_param('token', 'access_token')


class Endpoint(object):

    def __init__(self, base, suffix=None):
        """
        :param base: str
        :param suffix: str | None
        """
        self.url = base + (suffix if suffix else '')
        self.required = self._find_required(suffix)

    @staticmethod
    def _find_required(suffix):
        if not suffix:
            return set()
        return set(re.findall(r'{\s*(\w+)\s*}', suffix))

    def build_url(self, params):
        try:
            return self._build_url(params)
        except KeyError as e:
            raise ValueError("Unable to create url {0}, missing value: {1}".format(self.url, e))

    def _build_url(self, params):
        params = params.copy()
        required_params = {}
        for name in self.required:
            required_params[name] = params.pop(name)
        url = self.url.format(**required_params)
        if params:
            url = url + '?{0}'.format(urllib.urlencode(params))
        return url


class ResourceEndpoint(Logable):

    def __init__(self, dispatcher, endpoint, method, model_cls, params=None, data_params=None):
        """
        :type model_cls: cls
        :type dispatcher: resources.core.ApiDispatcher
        :type endpoint: Endpoint
        :type method: str
        :type params: Params
        :type data_params: Params
        """
        self.model_cls = model_cls
        self.dispatcher = dispatcher
        self.endpoint = endpoint
        self.method = method
        self.params = self._update_params_from_endpoint(endpoint, params)
        self.data = data_params

    @staticmethod
    def _update_params_from_endpoint(endpoint, params):
        if not params:
            params = Params()
        for name in endpoint.required:
            if name not in params:
                params.add_param(name, name)
        return params

    def __call__(self, **kwargs):
        translated_params = self.params.extract_and_translate(kwargs) if self.params else {}
        additional = self._create_additional_params(kwargs)
        translated_params.update(additional)
        translated_data = self.data.extract_and_translate(kwargs) if self.data else {}
        url = self.endpoint.build_url(translated_params)
        if len(translated_data) + len(translated_params) < len(kwargs) + len(additional):
            logging.warning("There are some unused attributes when calling {0}: {1}. Delivered params: {2}".format(
                self.method, self.endpoint.url, kwargs))
        request_kwargs = {}
        if len(translated_data) > 0:
            request_kwargs['data'] = translated_data
        return self.dispatcher.make_request(self.method, url, self.model_cls, **request_kwargs)

    def _create_additional_params(self, kwargs):
        return {}


class GetResourceEndpoint(ResourceEndpoint):

    def __init__(self, dispatcher, endpoint, model_cls, **kwargs):
        super(GetResourceEndpoint, self).__init__(dispatcher, endpoint, 'GET', model_cls, **kwargs)


class IndexResourceEndpoint(GetResourceEndpoint):

    def __init__(self, dispatcher, endpoint, model_cls, **kwargs):
        model_cls = ModelList.For(model_cls)
        super(IndexResourceEndpoint, self).__init__(dispatcher, endpoint, model_cls, **kwargs)

    def _create_additional_params(self, kwargs):
        page, per_page = get_pagination_params()
        return dict(offset=(page - 1) * per_page, limit=per_page)


class CreateResourceEndpoint(ResourceEndpoint):

    def __init__(self, dispatcher, endpoint, model_cls, **kwargs):
        super(CreateResourceEndpoint, self).__init__(dispatcher, endpoint, 'POST', model_cls, **kwargs)


class PatchResourceEndpoint(ResourceEndpoint):

    def __init__(self, dispatcher, endpoint, model_cls, **kwargs):
        super(PatchResourceEndpoint, self).__init__(dispatcher, endpoint, 'PATCH', model_cls, **kwargs)


class DeleteResourceEndpoint(ResourceEndpoint):

    def __init__(self, dispatcher, endpoint, **kwargs):
        super(DeleteResourceEndpoint, self).__init__(dispatcher, endpoint, 'DELETE', DeleteResponse, **kwargs)





