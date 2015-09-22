# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import cloudinary.uploader
import wtforms

from flask_babel import gettext
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import Length, Regexp, DataRequired

from flask_frontend.common.api_helper import ApiForm


class CreateTeamForm(ApiForm):

    name = wtforms.StringField(gettext('Name of team'), validators=[DataRequired(gettext("Field can't be empty"))])
    tag = wtforms.StringField(gettext('Tag, e.g. GGG'), validators=[DataRequired(gettext("Field can't be empty"))])
    description = wtforms.TextAreaField(gettext('Description'))

    def __init__(self, user, api, *args, **kwargs):
        super(CreateTeamForm, self).__init__(api, *args, **kwargs)
        self.user = user

    def _make_request(self):
        return self._api.teams.create(
            token=self.user.token, founder_id=self.user.id, name=self.name.data, description=self.description.data,
            tag=self.tag.data)


class EditTeamInfoForm(CreateTeamForm):

    def __init__(self, user, team, api, *args, **kwargs):
        super(EditTeamInfoForm, self).__init__(user, api, *args, **kwargs)
        self.team = team

    def set_data(self, team):
        self.name.data = team.name
        self.tag.data = team.tag
        self.description.data = team.description

    def _make_request(self):
        return self._api.teams.patch(
            team_id=self.team.id, token=self.user.token, name=self.name.data, description=self.description.data,
            tag=self.tag.data)


class ChangeTeamLogoForm(ApiForm):

    logo = FileField(gettext("Avatar"), validators=[
        FileRequired(message=gettext("You must specify file")),
        FileAllowed(['jpg', 'png'], gettext('Allowed extensions: .jpg, .png'))])

    def __init__(self, team_id, token, api, *args, **kwargs):
        super(ChangeTeamLogoForm, self).__init__(api, *args, **kwargs)
        self.team_id = team_id
        self.token = token

    def _make_request(self):
        result = cloudinary.uploader.upload_image(self.logo.data)
        self._api.teams.patch(team_id=self.team_id, token=self.token, image_url=result.url)
