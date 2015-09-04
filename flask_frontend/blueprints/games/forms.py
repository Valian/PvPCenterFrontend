# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import wtforms
from flask_babel import gettext
from wtforms.validators import Length

from flask_frontend.common.api_helper import ApiForm

nickname_field = wtforms.StringField(gettext('Nickname'), validators=[Length(3, message=gettext('At least 3 characters'))])

class GameJoinForm(ApiForm):

    nickname = nickname_field

    def __init__(self, api, token, game_id, user_id, *args, **kwargs):
        """
        :type game_ownership_id: int
        :return:
        """
        super(GameJoinForm, self).__init__(api, *args, **kwargs)
        self.token = token
        self.game_id = game_id
        self.user_id = user_id

    def _make_request(self):
        return self._api.game_ownerships.create(self.token, self.user_id, self.game_id, self.nickname)

    def _handle_errors(self, errors):
        self.server_errors.extend(errors.get_errors_for_field("nickname"))
        self.server_errors.extend(errors.get_errors_for_field("message"))

class GameUpdateForm(ApiForm):

    nickname = nickname_field

    def __init__(self, api, token, game_ownership_id, *args, **kwargs):
        super(GameUpdateForm, self).__init__(api, *args, **kwargs)
        self.game_ownership_id = game_ownership_id
        self.token = token

    def _make_request(self):
        return self._api.game_ownerships.update(self.token, self.game_ownership_id, self.nickname)

    def _handle_errors(self, errors):
        self.server_errors.extend(errors.get_errors_for_field("nickname"))
        self.server_errors.extend(errors.get_errors_for_field("message"))
