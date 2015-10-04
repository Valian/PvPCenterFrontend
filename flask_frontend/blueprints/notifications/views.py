# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask
import flask_login

from flask_frontend.common.pagination import Pagination
from flask_frontend.common.view_helpers.response_processors import PjaxView, template_view
from flask_frontend.common.view_helpers.routes import UrlRoute, UrlRoutes
from flask_frontend.common.api_helper import get_or_500, get_or_none


NUMBER_OF_NAVBAR_NOTIFICATIONS = 3


def create_routes():
    notifications_view = PjaxView('notifications_index.html', notifications_context)
    return UrlRoutes([
        UrlRoute('/', notifications_view, endpoint='index_view'),
        UrlRoute('/navbar', navbar_view)
    ])


def init_blueprint(blueprint, env):

    @blueprint.before_app_request
    def before_app_request():
        me = flask_login.current_user
        if me.is_authenticated():
            models = get_or_none(env.api.notifications.get, user_id=me.id, token=me.token, limit=0)
            count = models.unread_count if models is not None else 0
        else:
            count = 0
        flask.g.unread_notifications_count = count


@flask_login.login_required
def notifications_context(env):
    user = flask_login.current_user
    notificiations = get_or_500(env.api.notifications.get, token=user.token, user_id=user.id)
    pagination = Pagination.create_from_model_list(notificiations)
    return dict(notifications=notificiations, pagination=pagination)


@template_view('notifications_subview.html', notifications_context)
def navbar_view(notifications):
    return dict(notifications=notifications[:NUMBER_OF_NAVBAR_NOTIFICATIONS])
