# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask

from common.logable import Logable
from flask.ext.frontend.common.api_helper import AutoParams, get_or_500, get_or_none
from flask.ext.frontend.common.pagination import Pagination
from flask.ext.frontend.common.utils import pjax


class View(Logable):

    endpoint = None
    methods = None

    def __init__(self, env, *args, **kwargs):
        self.env = env

    def view_func(self, **kwargs):
        return None

    def before_request(self):
        pass

    def post_request(self):
        pass

    @classmethod
    def get_endpoint(cls):
        return cls.endpoint

    @classmethod
    def get_methods(cls):
        return cls.methods if cls.methods else ['GET']

    def process_params(self, **kwargs):
        return kwargs

    def process_response(self, response, **view_params):
        return response

    @classmethod
    def process_view_method(cls, method):
        return method

    @classmethod
    def as_view(cls, env, *args, **kwargs):

        def view_func(**view_params):
            view = cls(env, *args, **kwargs)
            view.before_request()
            processed_view_params = view.process_params(**view_params)
            response = view.view_func(**processed_view_params)
            final_response = view.process_response(response, processed_view_params)
            view.post_request()
            return final_response

        final_view_func = cls.process_view_method(view_func)
        return final_view_func


class TemplateRendererMixin(object):

    template = None

    def get_template(self, response, **view_params):
        return self.template

    def process_response(self, response, **view_params):
        response = super(TemplateRendererMixin, self).process_response(response, **view_params)
        if response is None or isinstance(response, dict):
            response = response or {}
            response.update(view_params)
            template = self.get_template(response, **view_params)
            return flask.render_template(template, **(response or {}))
        return response


class PjaxRendererMixin(object):

    template = None
    block = None

    def get_template(self, response, **view_params):
        return self.template

    def process_response(self, response, **view_params):
        response = super(PjaxRendererMixin, self).process_response(response, **view_params)
        if response is None or isinstance(response, dict):
            response = response or {}
            response.update(view_params)
            template = self.get_template(response, **view_params)
            return pjax(template, self.block, **(response or {}))
        return response


class ApiResourceMixin(object):

    model = None
    method = None
    allowed_params = None
    name = None

    def process_params(self, **kwargs):
        method = self.env.api.get_model_func(self.model, self.method)
        auto_params = AutoParams(method, allowed_params=self.allowed_params)
        response = auto_params.perform_request()
        self.add_response_to_params(response, kwargs)
        return kwargs

    def add_response_to_params(self, response, params):
        name = self.get_context_name()
        params[name] = get_or_500(response)

    def get_context_name(self):
        return self.name


class ApiResourceGetMixin(ApiResourceMixin):

    method = 'get_single'

    def get_context_name(self):
        name = super(ApiResourceGetMixin, self).get_context_name()
        if name is None:
            return self.model.__name__.lower()
        return name


class ApiResourceIndexMixin(ApiResourceMixin):

    method = 'get'

    def add_response_to_params(self, response, params):
        super(ApiResourceIndexMixin, self).add_response_to_params(response, params)
        model = get_or_none(response)
        params['pagination'] = Pagination.create_from_model_list(model)

    def get_context_name(self):
        name = super(ApiResourceIndexMixin, self).get_context_name()
        if name is None:
            return self.model.__name__.lower() + "s"
        return name


class RestrictionMixin(object):

    restrictions = []

