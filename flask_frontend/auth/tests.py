# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from unittest import TestCase
from flask.ext.frontend.app import create_app
from flask_frontend.config import get_test_config


class AuthTests(TestCase):

    def setUp(self):
        config = get_test_config()
        self.app = create_app(config)
        self.client = self.app.test_client()

    def test(self):
        pass
