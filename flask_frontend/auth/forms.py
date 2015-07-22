# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)


import flask_wtf
import wtforms

from flask_babel import gettext
from wtforms.validators import Length, Email, Regexp
from flask.ext.frontend.common.api_helper import ApiForm
from flask_frontend.auth.user import User


class LoginForm(ApiForm):

    email = wtforms.StringField(gettext('Email'), validators=[Email(message=gettext('Invalid email'))])
    password = wtforms.PasswordField(gettext('Password'), validators=[
        Length(8, message=gettext('Min %(num)d characters', num=8))])

    def _handle_errors(self, errors):
        self.email.errors.extend(errors.get_errors_for_field('email'))
        self.password.errors.extend(errors.get_errors_for_field('password'))
        self.server_errors = errors.get_errors_for_field('message')

    def _make_request(self):
        return self._api.login.post(self.email.data, self.password.data, model=User)


class RegisterForm(ApiForm):

    login = wtforms.StringField(gettext('Login'), validators=[
        Length(8, message=gettext('Min %(num)d characters', num=8)),
        Regexp(r'^[\w_]+$', message=gettext("Only alphanumeric characters!"))])
    email = wtforms.StringField(gettext('Email'), validators=[Email(message=gettext('Invalid email'))])
    password = wtforms.PasswordField(gettext('Password'), validators=[
        Length(8, message=gettext('Min %(num)d characters', num=8))])
    password_again = wtforms.PasswordField(gettext('Repeat password'), validators=[
        Length(8, message=gettext('Min %(num)d characters', num=8))])

    def _additional_validation(self):
        if self.password.data != self.password_again.data:
            self.password_again.errors.append(gettext('Passwords do not match!'))
            return False
        return True

    def _handle_errors(self, errors):
        pass

    def _make_request(self):
        return self._api.users.post(self.login.data, self.email.data, self.password.data, model=User)

