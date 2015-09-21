# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)


import flask_login

from flask_frontend.common.pagination import Pagination
from flask_frontend.common.view_helpers.response_processors import PjaxView, template_view
from flask_frontend.common.view_helpers.routes import UrlRoute, UrlRoutes
from flask_frontend.common.api_helper import get_or_500


NUMBER_OF_NAVBAR_NOTIFICATIONS = 3


def create_routes():
    notifications_view = PjaxView('notifications_index.html', notifications_context)
    return UrlRoutes([
        UrlRoute('/', notifications_view, endpoint='index_view'),
        UrlRoute('/navbar', navbar_view)
    ])


@flask_login.login_required
def notifications_context(env):
    user = flask_login.current_user
    notificiations = get_or_500(env.api.notifications.get, user.token, user.id)
    pagination = Pagination.create_from_model_list(notificiations)
    return dict(notifications=notificiations, pagination=pagination)


@template_view('notifications_subview.html', notifications_context)
def navbar_view(notifications):
    return dict(notifications=notifications[:NUMBER_OF_NAVBAR_NOTIFICATIONS])
