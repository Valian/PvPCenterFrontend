# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import wtforms

from flask_babel import gettext
from flask_frontend.common.const import SEX
from wtforms.validators import Email, EqualTo
from api.models import User

from flask_frontend.common.api_helper import ApiForm


class ChangeEmailForm(ApiForm):

    email = wtforms.StringField(gettext('New email'), validators=[Email(message=gettext('Invalid email'))])
    repeat = wtforms.StringField(gettext('Repeat'), validators=[
        EqualTo('email', gettext('Emails are not equal'))])

    def __init__(self, api, user, *args, **kwargs):
        """
        :type api: PvPCenterApi
        :type user: User
        """
        super(ChangeEmailForm, self).__init__(api, *args, **kwargs)
        self.user_id = user.id
        self.token = user.token


    def _make_request(self):
        return self._api.users.patch(self.user_id, self.token, email=self.email.data)


class ChangeBasicDataForm(ApiForm):

    sex = wtforms.SelectField(gettext('Sex'), coerce=int, choices=[
        (SEX.UNDEFINED, gettext('Undefined')), (SEX.MALE, gettext('Male')), (SEX.FEMALE, gettext('Female'))])
    nationality = wtforms.SelectField(gettext('Nationality'), choices=[('pl', 'Poland'), ('en', "Great Britain")])
    birthdate = wtforms.DateField(gettext('Birthday'))
    description = wtforms.TextAreaField(gettext('About me'), default='None')

    def __init__(self, api, user, *args, **kwargs):
        """
        :type api: PvPCenterApi
        :type user: User
        """
        self.user_id = user.id
        self.token = user.token
        super(ChangeBasicDataForm, self).__init__(api, *args, **kwargs)

    def set_data(self, user):
        self.sex.data = user.sex
        self.birthdate.data = user.birthdate
        self.nationality.data = user.nationality
        self.description.data = user.description

    def _make_request(self):
        return self._api.users.patch(
            self.user_id, self.token,
            sex=self.sex.data,
            nationality=self.nationality.data,
            birthdate=self.birthdate.data,
            description=self.description.data)

