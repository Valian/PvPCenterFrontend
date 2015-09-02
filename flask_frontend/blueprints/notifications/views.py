# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)


import flask
import flask_login
from flask.ext.frontend.blueprints.notifications import notifications_blueprint
from flask.ext.frontend.common.api_helper import get_or_500

NUMBER_OF_NAVBAR_NOTIFICATIONS = 3


@notifications_blueprint.route('')
@flask_login.login_required
def index_view():
    user = flask_login.current_user
    notificiations = get_or_500(notifications_blueprint.api.notifications.get, user.token, user.id)
    return flask.render_template('notifications_index.html', notifications=notificiations)


@notifications_blueprint.route('/navbar')
@flask_login.login_required
def navbar_view():
    user = flask_login.current_user
    notificiations = get_or_500(notifications_blueprint.api.notifications.get, user.token, user.id)
    newest = notificiations[:NUMBER_OF_NAVBAR_NOTIFICATIONS]
    return flask.render_template('notifications_subview.html', notifications=newest)
