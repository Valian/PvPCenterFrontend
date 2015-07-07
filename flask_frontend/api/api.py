# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import requests
from requests.auth import HTTPBasicAuth
from models import Game

from common.logable import Logable


class Api(Logable):

    def __init__(self, base_url, login, password):
        self.password = password
        self.login = login
        self.base_url = base_url

    def get_games(self):
        try:
            response = requests.get(self.base_url + '/games', auth=HTTPBasicAuth(self.login, self.password))
            if response.ok:
                return map(Game.from_json, response.json())
            else:
                self.log_error("Error while downloading games. More info: " + str(response.reason))

        except ValueError as e:
            self.log_error("Error while downloading games. More info: " + str(e))

    def get_game(self, id):
        try:
            response = requests.get(self.base_url + '/games/' + id, auth=HTTPBasicAuth(self.login, self.password))
            if response.ok:
                return Game.from_json(response.json())
            else:
                self.log_error("Error while downloading games. More info: " + str(response.reason))

        except ValueError as e:
            self.log_error("Error while downloading games. More info: " + str(e))

