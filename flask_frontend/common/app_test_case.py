# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from unittest import TestCase

from flask_frontend.app import create_app
from flask_frontend.config import get_test_config


class AppTestCase(TestCase):

    def get_config(self, config=None):
        return get_test_config(config)

    def setUp(self):
        config = self.get_config()
        self.app = create_app(config)
        self.client = self.app.test_client()
        self.context = self.app.test_request_context()
        self.context.push()

    def tearDown(self):
        self.context.pop()
