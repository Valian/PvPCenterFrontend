# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask

import mock
from resources.core import ApiResult
from resources.mock import create_mock_for
from resources.models import ModelList, Notification
from flask_frontend.common.app_test_case import AppTestCase, logged_in


@mock.patch('flask_frontend.blueprints.notifications.views.notifications_blueprint.api')
class NotificationTests(AppTestCase):

    def test_get_notifications_fails_without_login(self, api):
        api.notifications.get.return_value = ApiResult(data=create_mock_for(ModelList.For(Notification)))
        self.client.get(flask.url_for('notifications.index_view'), expect_errors=True)

    @logged_in
    def test_get_notifications_calls_api(self, user, api):
        api.notifications.get.return_value = ApiResult(create_mock_for(ModelList.For(Notification)))
        response = self.client.get(flask.url_for('notifications.index_view'))
        self.assertTrue(api.notifications.get.called)
        self.assertIsInstance(response.context['notifications'], list)


