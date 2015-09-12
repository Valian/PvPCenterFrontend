# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import cloudinary.uploader

import wtforms
from flask_babel import gettext
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import Email, EqualTo
from api.api import ApiException

from api.constants import NATIONALITIES
from api.models import User
from flask_frontend.common.const import SEX
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

    sex = wtforms.SelectField(gettext('Sex'), choices=[(SEX.MALE, gettext('Male')), (SEX.FEMALE, gettext('Female'))])
    nationality = wtforms.SelectField(gettext('Nationality'), choices=NATIONALITIES.CODES)
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


class ChangeAvatarForm(ApiForm):

    avatar = FileField(gettext("Avatar"), validators=[
        FileRequired(message=gettext("You must specify file")),
        FileAllowed(['jpg', 'png'], gettext('Allowed extensions: .jpg, .png'))])

    def __init__(self, user_id, token, api, *args, **kwargs):
        super(ChangeAvatarForm, self).__init__(api, *args, **kwargs)
        self.user_id = user_id
        self.token = token

    def _make_request(self):
        result = cloudinary.uploader.upload_image(self.avatar.data)
        self._api.users.patch(self.user_id, self.token, image_url=result.url)
