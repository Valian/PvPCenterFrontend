# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import wtforms

from flask_babel import gettext
from wtforms.validators import Length, Email
from wtforms.validators import Regexp

from flask_frontend.common.api_helper import ApiForm


class EditProfileForm(ApiForm):

    nickname = wtforms.StringField(gettext('Nickname'), validators=[
        Length(8, message=gettext('Min %(num)d characters', num=8)),
        Regexp(r'^[\w_]+$', message=gettext("Only alphanumeric characters!"))])
    email = wtforms.StringField(gettext('Email'), validators=[Email(message=gettext('Invalid email'))])

    def __init__(self, api, user_id, token, *args, **kwargs):
        super(EditProfileForm, self).__init__(api, *args, **kwargs)
        self.user_id = user_id
        self.token = token

    def _handle_errors(self, errors):
        self.nickname.errors.extend(errors.get_errors_for_field("nickname"))
        self.email.errors.extend(errors.get_errors_for_field("email"))
        self.server_errors.extend(errors.get_errors_for_field("message"))

    def _make_request(self):
        return self._api.user.patch(self.user_id, self.token, self.nickname.data, self.email.data)
