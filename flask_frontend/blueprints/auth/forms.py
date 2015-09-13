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
    password = wtforms.PasswordField(gettext('Password'))
    remember_me = wtforms.BooleanField(gettext('Remember me'), default=False)

    def _make_request(self):
        return self._api.users.login(self.email.data, self.password.data, model=User)


class RegisterForm(ApiForm):

    nickname = wtforms.StringField(gettext('Login'))
    email = wtforms.StringField(gettext('Email'), validators=[Email(message=gettext('Invalid email'))])
    password = wtforms.PasswordField(gettext('Password'))
    password_again = wtforms.PasswordField(gettext('Repeat password'), validators=[
        EqualTo('password', message=gettext('Passwords must match'))])
    rules = wtforms.BooleanField(gettext("Do you accept our rules"), validators=[
        DataRequired('')])
    spam = wtforms.BooleanField(gettext("Do you want spam"))

    def _make_request(self):
        return self._api.users.post(self.nickname.data, self.email.data, self.password.data, model=User)

