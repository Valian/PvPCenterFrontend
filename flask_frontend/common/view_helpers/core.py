# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import functools
import inspect
import flask

from common.logable import Logable
from common.utils import to_iter
from flask_frontend.common.view_helpers.restrictions import RestrictionRegistry
from flask_frontend.common.utils import get_true_argspec


class ViewEnvironment(object):

    def __init__(self, api, config):
        """
        :type api: resources.api.PvPCenterApi
        :type config: dict
        """
        self.config = config
        self.api = api


def empty_func():
    pass


class BaseView(Logable):

    def __init__(self, context_creators=None, response_processor=None, view_func=None, decorators=None):
        """
        :type context_creators: list[ContextCreator] | list[(env, **kwargs) -> dict]
        :type response_processor: flask_frontend.common.view_helpers.response_processors.ResponseProcessor | callable(response, dict)
        :type view_func: (env, **kwargs) -> (dict | flask.Response)
        :type decorators: list[(func1) -> func2]
        """
        self.decorators = decorators or []
        self.response_processor = response_processor
        self.context_creators = to_iter(context_creators) if context_creators else []
        self.view_func = view_func or empty_func
        self.view_func_args = get_true_argspec(self.view_func)[0]

    def __call__(self, f):
        self.view_func = self._get_function(f)
        self.view_func_args = get_true_argspec(self.view_func)[0]
        return self

    @staticmethod
    def _get_function(f):
        if not f:
            return None
        func = f if inspect.ismethod(f) or inspect.isfunction(f) else f.__call__
        return func

    def as_view(self, env, restrictions, menu):
        self._init_context(env)
        if menu:
            self.context_creators.append(menu)

        @functools.wraps(self.view_func)
        def proxy(**view_args):
            can_proceed = RestrictionRegistry.can_proceed(restrictions or [], env, view_args)
            if not can_proceed:
                flask.abort(403)
            view_args = self.create_context(env, view_args)
            if not isinstance(view_args, dict):
                return view_args
            response = self.call_view_method(env, view_args)
            if isinstance(response, dict):
                view_args.update(response)
                response = None
            response = self.process_response(response, view_args)
            return response

        for decorator in self.decorators:
            proxy = decorator(proxy)
        return proxy

    def _init_context(self, env):
        for creator in self.context_creators:
            try:
                creator.init(env)
            except AttributeError:
                pass

    def call_view_method(self, env, view_args):
        expected_kwargs = {key: value for key, value in view_args.iteritems() if key in self.view_func_args}
        if 'env' in self.view_func_args:
            expected_kwargs['env'] = env
        return self.view_func(**expected_kwargs)

    def create_context(self, env, view_args):
        creators_kwargs = view_args.copy()
        result_kwargs = {}
        for creator in self.context_creators:
            new = creator(env, **creators_kwargs)
            if not isinstance(new, dict):
                return new
            result_kwargs.update(new)
            creators_kwargs.update(new)
        return result_kwargs

    def process_response(self, response, context):
        if not response and self.response_processor:
            return self.response_processor(response, context)
        return response

view = BaseView
