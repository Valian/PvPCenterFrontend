# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask_babel import gettext

import flask_wtf
import wtforms
from api.api import PvPCenterApi, ApiException
from flask_frontend.auth.user import User


class LoginForm(flask_wtf.Form):

    email = wtforms.StringField(gettext('Email'), validators=[
        wtforms.validators.Email(message=gettext('Invalid email'))])
    password = wtforms.PasswordField(gettext('Password'), validators=[
        wtforms.validators.Length(8, message=gettext('Min %(num)d characters', num=8))])

    def __init__(self, api, *args, **kwargs):
        """
        :type api: PvPCenterApi
        """
        super(LoginForm, self).__init__(*args, **kwargs)
        self._api = api
        self.user = None
        self.server_errors = []

    def validate(self):
        rv = super(LoginForm, self).validate()
        if not rv:
            return False

        try:
            api_result = self._api.login_user(self.email.data, self.password.data, model=User)
            if api_result.ok:
                self.user = api_result.data
                return True
            self.email.errors.extend(api_result.errors.get_errors_for_field('email'))
            self.password.errors.extend(api_result.errors.get_errors_for_field('password'))
            self.server_errors = api_result.errors.get_errors_for_field('message')
            return False
        except ApiException as e:
            self.server_errors = [gettext("Server error, try again later")]
            return False


