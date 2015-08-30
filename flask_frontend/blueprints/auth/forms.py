# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import wtforms

from flask_babel import gettext
from wtforms.validators import Length, Email, Regexp, DataRequired, EqualTo

from flask_frontend.common.api_helper import ApiForm
from flask_frontend.common.redirect import RedirectFormMixin
from .user import User


class LoginForm(RedirectFormMixin, ApiForm):

    email = wtforms.StringField(gettext('Email'), validators=[Email(message=gettext('Invalid email'))])
    password = wtforms.PasswordField(gettext('Password'), validators=[
        Length(8, message=gettext('Min %(num)d characters', num=8))])
    remember_me = wtforms.BooleanField(gettext('Remember me'), default=False)

    def _handle_errors(self, errors):
        self.email.errors.extend(errors.get_errors_for_field('email'))
        self.password.errors.extend(errors.get_errors_for_field('password'))
        self.server_errors = errors.get_errors_for_field('message')

    def _make_request(self):
        return self._api.users.login(self.email.data, self.password.data, model=User)


class RegisterForm(ApiForm):

    login = wtforms.StringField(gettext('Login'), validators=[
        Length(8, message=gettext('Min %(num)d characters', num=8)),
        Regexp(r'^[\w_]+$', message=gettext("Only alphanumeric characters!"))])
    email = wtforms.StringField(gettext('Email'), validators=[
        Email(message=gettext('Invalid email'))])
    password = wtforms.PasswordField(gettext('Password'), validators=[
        Length(8, message=gettext('Min %(num)d characters', num=8))])
    password_again = wtforms.PasswordField(gettext('Repeat password'), validators=[
        EqualTo('password', message=gettext('Passwords must match'))])
    rules = wtforms.BooleanField(gettext("Do you accept our rules"), validators=[
        DataRequired('')])
    spam = wtforms.BooleanField(gettext("Do you want spam"))

    def _handle_errors(self, errors):
        pass

    def _make_request(self):
        return self._api.users.post(self.login.data, self.email.data, self.password.data, model=User)

