# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import inspect

from abc import ABCMeta, abstractmethod
import flask

import flask_login

from common.logable import Logable
from flask_frontend.common.api_helper import get_or_404
from flask_frontend.common.pagination import Pagination
from flask_frontend.common.view_helpers.core import empty_func, BaseView


class ContextCreator(Logable):

    __metaclass__ = ABCMeta

    def __call__(self, env, **kwargs):
        """
        :type env: flask_frontend.common.view_helpers.core.ViewEnvironment
        """
        return self.create_context(env, **kwargs)

    def init(self, env):
        """
        :type env: flask_frontend.common.view_helpers.core.ViewEnvironment
        :rtype: None
        """
        pass

    @abstractmethod
    def create_context(self, env, **kwargs):
        """
        :type env: flask_frontend.common.view_helpers.core.ViewEnvironment
        :rtype: dict
        """
        return kwargs


class ApiResourceContext(ContextCreator):

    def __init__(self, model, method_name, out_name, allowed_params=None, allow_all_params=False, include_token=True,
                 params_translators=None):
        """
        :type model: subclass(api.api.ModelBase)
        :type method_name: str
        :type out_name: str
        :type allowed_params: list[str]
        :type allow_all_params: bool
        :type include_token: bool
        :type params_translators: dict[str:(env, **kwargs) -> Any] | dict[str: str]
        """
        self.params_translators = params_translators or {}
        self.allowed_params = allowed_params or []
        self.include_token = include_token
        self.out_name = out_name
        self.allow_all_params = allow_all_params
        self.method_name = method_name
        self.model = model
        self.view_method = None

    def create_context(self, env, **kwargs):
        params = {}
        self._translate_params(env, kwargs)
        for name in self.allowed_params:
            if name in kwargs:
                params[name] = kwargs[name]
                continue
            self._add_from_request_args(name, params)
        if self.include_token:
            self._add_token(params)
        return {self.out_name: get_or_404(self.view_method, **params)}

    def _translate_params(self, env, params):
        if len(self.params_translators) > 0:
            for name, translator in self.params_translators.iteritems():
                if callable(translator):
                    params[name] = translator(env, params)
                else:
                    params[name] = translator

    @staticmethod
    def _add_token(params):
        user = flask_login.current_user
        params['token'] = user.token if user.is_authenticated() else None

    @staticmethod
    def _add_from_request_args(name, params):
        param = flask.request.args.get(name)
        if param and param not in params:
            params[name] = param

    def init(self, env):
        self.view_method = env.api.get_model_func(self.model, self.method_name)
        self.allowed_params = self._get_allowed_params()

    def _get_allowed_params(self):
        available_params = self.view_method.params.get_available() | self.view_method.data.get_available()
        allowed = set()
        for param in available_params:
            if param in ['self', 'model', 'token']:
                continue
            if self.allow_all_params or param in self.allowed_params or param in self.params_translators:
                allowed.add(param)
        if 'token' not in available_params:
            self.include_token = False
        return allowed


class ApiResourceGet(ApiResourceContext):

    def __init__(self, model, **kwargs):
        """
        :type model: subclass(api.api.ModelBase)
        """
        name = model.__name__.lower()
        kwargs['allowed_params'] = kwargs.get('allowed_params', [])
        kwargs['allowed_params'].append(name + "_id")
        super(ApiResourceGet, self).__init__(model, 'get_single', name, **kwargs)


class ApiResourceIndex(ApiResourceContext):

    def __init__(self, model, **kwargs):
        """
        :type model: subclass(api.api.ModelBase)
        """
        name = model.__name__.lower() + 's'
        super(ApiResourceIndex, self).__init__(model, 'get', name, **kwargs)

    def create_context(self, env, **kwargs):
        result = super(ApiResourceIndex, self).create_context(env, **kwargs)
        result['pagination'] = Pagination.create_from_model_list(result[self.out_name])
        return result


class ModelView(BaseView):

    def __init__(self, model, response_processor=None, view_func=None, **kwargs):
        super(ModelView, self).__init__([ApiResourceGet(model, **kwargs)], response_processor, view_func)
        self.model = model

    def as_view(self, env):
        func = super(ModelView, self).as_view(env)
        if func.__name__ == empty_func.__name__:
            func.__name__ = "{0}_view".format(self.model.__name__.lower())
        return func


class IndexView(BaseView):

    def __init__(self, model, response_processor=None, view_func=None, **kwargs):
        super(IndexView, self).__init__([ApiResourceIndex(model, **kwargs)], response_processor, view_func)
        self.model = model

    def as_view(self, env):
        func = super(IndexView, self).as_view(env)
        if func.__name__ == empty_func.__name__:
            func.__name__ = "{0}s_view".format(self.model.__name__.lower())
        return func

model_view = ModelView
index_view = IndexView
