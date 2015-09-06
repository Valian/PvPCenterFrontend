# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
from flask.ext.babel import gettext
import wtforms
from wtforms.validators import Length, Regexp, DataRequired
from flask.ext.frontend.common.api_helper import ApiForm


class CreateTeamForm(ApiForm):

    name = wtforms.StringField(gettext('Name of team'), validators=[
        DataRequired(gettext("Field can't be empty")),
        Length(min=5, message=gettext("At least %(num)s characters", num=5)),
        Regexp(r'\w*', message="Only letters and digits!")])
    tag = wtforms.StringField(gettext('Tag, e.g. GGG'), validators=[
        DataRequired(gettext("Field can't be empty")),
        Length(min=2, max=8, message=gettext("Between %(min)s and %(max)s characters", min=2, max=8)),
        Regexp(r'[A-Z\d]+', message="Only big letters and digits!")])
    description = wtforms.TextAreaField(gettext('Description'), validators=[
        Regexp(r'[\w\s]*', message="Only letters and digits!")])

    def __init__(self, token, api, *args, **kwargs):
        super(CreateTeamForm, self).__init__(api, *args, **kwargs)
        self.token = token

    def _make_request(self):
        return self._api.teams.post(self.token, self.name.data, self.description.data, self.tag.data)
