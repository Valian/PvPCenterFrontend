# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
from common.logable import Logable


class InvalidJsonException(Exception):
    pass

class Game(object):

    def __init__(self, id, name):
        self.id = id
        self.name = name

    @staticmethod
    def from_json(json):
        """
        :type json: dict
        :rtype: Game
        """
        try:
            return Game(json['id'], json['name'])
        except AttributeError as e:
            raise InvalidJsonException('Error while creating Game object, more info: {0}'.format(e))

    def __unicode__(self):
        return 'Game {0}, id = {1}'.format(self.name, self.id)



