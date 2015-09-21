# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)


from abc import ABCMeta, abstractmethod
import flask

from common.logable import Logable
from flask.ext.frontend.common.utils import pjax
from flask.ext.frontend.common.view_helpers.core import BaseView


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


class TemplateView(BaseView):

    def __init__(self, template, context_creators=None, **kwargs):
        renderer = TemplateRenderer(template)
        super(TemplateView, self).__init__(context_creators, renderer, **kwargs)


class PjaxView(BaseView):

    def __init__(self, template, context_creators=None, block='pjax_content', **kwargs):
        renderer = PjaxRenderer(template, block)
        super(PjaxView, self).__init__(context_creators, renderer, **kwargs)

pjax_view = PjaxView
template_view = TemplateView
