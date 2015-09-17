# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask
from flask.ext.classy import FlaskView, get_interesting_members, get_true_argspec
import functools
import re
from common.logable import Logable
from flask.ext.frontend.common.utils import pjax


def route(endpoint=None, **kwargs):
    def decorator(f):
        f._routing_info = (endpoint, kwargs)
        return f
    return decorator


def register(app):

    def wrapper(cls):
        cls.register(app)
        return cls
    return wrapper


class BaseView(Logable):

    decorators = []

    def create_context(self, **kwargs):
        return {}

    def after_request(self, name, response, context):
        return response

    @classmethod
    def register(cls, app):
        members = get_interesting_members(BaseView, cls)
        prefix = cls.get_rule_prefix()
        for name, original_method in members:
            method = cls.make_proxy_method(name)
            rule, rule_kwargs = cls.build_rule(prefix, original_method, name)
            app.add_url_rule(rule, name, method, **rule_kwargs)

    @classmethod
    def get_rule_prefix(cls):
        routing_info = getattr(cls.create_context, '_routing_info', None)
        if routing_info and routing_info[0]:
            return routing_info[0]
        return ''

    @classmethod
    def build_rule(cls, prefix, method, name):
        rule_parts = []
        if prefix:
            rule_parts.append(prefix)

        routing_info = getattr(method, '_routing_info', None)
        if routing_info and routing_info[0]:
            rule_parts.append(routing_info[0])
        elif name.upper() not in ['get', 'index']:
            rule_parts.append(name)

        rule_kwargs = routing_info[1] if routing_info else {}
        result = "/%s" % "/".join(rule_parts)
        return re.sub(r'(/)\1+', r'\1', result), rule_kwargs

    @classmethod
    def make_proxy_method(cls, name):
        i = cls()
        view = getattr(i, name)
        args = get_true_argspec(view)[0]

        if cls.decorators:
            for decorator in cls.decorators:
                view = decorator(view)

        @functools.wraps(view)
        def proxy(**view_args):

            view_args = i.create_context(**view_args)

            expected_kwargs = {key: value for key, value in view_args.iteritems() if key in args}

            response = view(**expected_kwargs)

            response = i.after_request(name, response, view_args) or response
            return response

        return proxy


class TemplateView(BaseView):

    template = None

    def after_request(self, name, response, context):
        if response is None:
            return flask.render_template(self.template, **context)
        return response


class PjaxView(BaseView):

    def after_request(self, name, response, context):
        if response is None:
            return pjax(self.template, **context)
        return response

