# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import inspect

from abc import ABCMeta, abstractmethod
import functools

import flask

from common.logable import Logable
from flask.ext.frontend.common.api_helper import get_or_404
from flask.ext.frontend.common.pagination import Pagination
from flask.ext.frontend.common.utils import pjax, get_true_argspec


class UrlRoute(object):

    def __init__(self, route, view, **kwargs):
        self.view = view
        self.route = route
        self.kwargs = kwargs


class UrlRoutes(object):

    def __init__(self, routes):
        """
        :type routes: list[UrlRoute]
        :return:
        """
        self.routes = routes

    def register(self, app, env):
        """
        :type app: flask.Flask | flask.Blueprint
        :type env: ViewEnvironment
        """
        for route in self.routes:
            """:type : UrlRoute"""
            app.add_url_rule(route.route, view_func=route.view.as_view(env), **route.kwargs)


class ViewEnvironment(object):

    def __init__(self, api, config):
        self.config = config
        self.api = api


class ContextCreator(Logable):

    __metaclass__ = ABCMeta

    def __call__(self, env, **kwargs):
        return self.create_context(env, **kwargs)

    @abstractmethod
    def create_context(self, env, **kwargs):
        return kwargs


class ApiGetMethod(ContextCreator):

    def __init__(self, param_name, api_method, allowed_params=None, allow_all_params=False):
        self.name = param_name
        self.api_method = api_method
        self.allowed_names = self._get_allowed_params(api_method, allowed_params, allow_all_params)

    def create_context(self, env, **params):
        for name in self.allowed_names:
            param = flask.request.args.get(name)
            if param and param not in params:
                params[name] = param
        return {self.name: get_or_404(self.api_method, **params)}

    @staticmethod
    def _get_allowed_params(api_method, allowed_params, allow_all_params):
        available_params = inspect.getargspec(api_method).args
        allowed = []
        for param in available_params:
            if param in ['self', 'model']:
                continue
            if allow_all_params or param in allowed_params:
                allowed.append(param)
        return allowed


class ApiIndexMethod(ApiGetMethod):

    def create_context(self, env, **kwargs):
        result = super(ApiIndexMethod, self).create_context(env, **kwargs)
        result['pagination'] = Pagination.create_from_model_list(result[self.name])
        return result

class ResponseProcessor(Logable):

    __metaclass__ = ABCMeta

    def __call__(self, response, context):
        return self.process_response(response, context)

    @abstractmethod
    def process_response(self, response, context):
        return response


class TemplateRenderer(ResponseProcessor):

    def __init__(self, template):
        self.template = template

    def process_response(self, response, context):
        return flask.render_template(self.template, **context)


class PjaxRenderer(ResponseProcessor):

    def __init__(self, template, block='pjax_content'):
        self.template = template
        self.block = block

    def process_response(self, response, context):
        return pjax(self.template, self.block, **context)


def empty_func():
    pass


class BaseView(Logable):

    def __init__(self, context_creator=None, response_processor=None):
        self.response_processor = response_processor
        self.context_creator = context_creator
        self.f = empty_func
        self.f_args = []

    def __call__(self, f):
        self.f = self._get_function(f)
        self.f_args = get_true_argspec(self.f)[0]
        return self

    @staticmethod
    def _get_function(f):
        if not f:
            return None
        func = f if inspect.ismethod(f) or inspect.isfunction(f) else f.__call__
        return func

    def as_view(self, env):
        @functools.wraps(self.f)
        def proxy(**view_args):
            view_args = self.create_context(env, view_args)
            if not isinstance(view_args, dict):
                return view_args
            response = self.call_view_method(env, view_args)
            if isinstance(response, dict):
                view_args.update(response)
                response = None
            response = self.process_response(response, view_args)
            return response
        return proxy

    def call_view_method(self, env, view_args):
        expected_kwargs = {key: value for key, value in view_args.iteritems() if key in self.f_args}
        if 'env' in self.f_args:
            expected_kwargs['env'] = env
        return self.f(**expected_kwargs)

    def create_context(self, env, view_args):
        if self.context_creator:
            return self.context_creator(env, **view_args)
        return view_args

    def process_response(self, response, context):
        if not response and self.response_processor:
            return self.response_processor(response, context)
        return response


class TemplateView(BaseView):

    def __init__(self, template, context_creator=None):
        renderer = TemplateRenderer(template)
        super(TemplateView, self).__init__(context_creator, renderer)


class PjaxView(BaseView):

    def __init__(self, template, context_creator=None, block='pjax_content'):
        renderer = PjaxRenderer(template, block)
        super(PjaxView, self).__init__(context_creator, renderer)


pjax_view = PjaxView
template_view = TemplateView
view = BaseView