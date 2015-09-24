# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask

from api.models import Notification
from flask_frontend.common.app_test_case import AppTestCase, logged_in, mock_api


class NotificationTests(AppTestCase):

    @mock_api(Notification, 'get')
    def test_get_notifications_fails_without_login(self, get):
        self.client.get(flask.url_for('notifications.index_view'), expect_errors=True)

    @mock_api(Notification, 'get')
    @logged_in()
    def test_get_notifications_calls_api(self, get, user):
        response = self.client.get(flask.url_for('notifications.index_view'))
        self.assertTrue(get.called)
        self.assertIsInstance(response.context['notifications'], list)


