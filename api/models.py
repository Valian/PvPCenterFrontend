# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from abc import ABCMeta, abstractmethod

from common.utils import abstractclassmethod, to_iter


class UnableToParseException(Exception):

    def __init__(self, cls, e):
        super(UnableToParseException, self).__init__(
            'Unable to create {0} object, more info: {1}'.format(cls, e))


class ModelBase(object):

    __metaclass__ = ABCMeta

    @classmethod
    def from_json(cls, json):
        try:
            return cls._from_json(json)
        except (TypeError, AttributeError, KeyError) as e:
            raise UnableToParseException(cls, e)

    @abstractclassmethod
    def _from_json(cls, json):
        raise NotImplementedError

    @abstractmethod
    def to_json(self):
        raise NotImplementedError

    @abstractmethod
    def __str__(self):
        return super(ModelBase, self).__str__()


class ModelList(list):

    def __init__(self, data, total):
        super(ModelList, self).__init__(data)
        self.total = total

    class For(object):

        TOTAL_FIELD = "total"
        DATA_FIELD = "models"

        def __init__(self, model):
            """
            :type model: ModelBase
            """
            self.model = model

        def from_json(self, json):
            try:
                total = json[self.TOTAL_FIELD]
                data = map(self.model.from_json, json[self.DATA_FIELD])
                return ModelList(data, total)
            except (TypeError, AttributeError, KeyError) as e:
                raise UnableToParseException(ModelList, e)


class Game(ModelBase):

    __slots__ = ('id', 'name')

    def __init__(self, id, name):
        self.id = id
        self.name = name

    @classmethod
    def _from_json(cls, json):
        return cls(json['id'], json['name'])

    def to_json(self):
        return {'id': self.id, 'name': self.name}

    def __str__(self):
        return '[Game {0}:{1}]'.format(self.id, self.name)


class UserGameOwnership(ModelBase):

    def __init__(self, id, nickname, game):
        self.id = id
        self.nickname = nickname
        self.game = game

    def to_json(self):
        return {'id': self.id, 'nickname': self.nickname, 'game': self.game.to_json()}

    @classmethod
    def _from_json(cls, json):
        game = Game.from_json(json['game'])
        return cls(json['id'], json.get('nickname'), game)

    def __str__(self):
        return '[UserGameOwnership {0}:{1} {2}]'.format(self.id, self.nickname, self.game)


class User(ModelBase):

    def __init__(self, id, name, email, token, game_ownerships):
        self.id = id
        self.name = name
        self.email = email
        self.token = token
        self.game_ownerships = game_ownerships

    @classmethod
    def _from_json(cls, json):
        game_ownerships = [UserGameOwnership.from_json(go) for go in json.get('game_ownerships', [])]
        return cls(json['id'], json['nickname'], json['email'], json.get('access_token'), game_ownerships)

    def to_json(self):
        game_ownerships = [go.to_json() for go in self.game_ownerships]
        return {
            'id': self.id, 'nickname': self.name, 'email': self.email, 'access_token': self.token,
            'game_ownerships': game_ownerships}

    def __str__(self):
        return '[User {0}: {1} - {2}, owned games: {3}]'.format(self.id, self.name, self.email, self.game_ownerships)


class Error(ModelBase):

    __slots__ = ('message',)

    def __init__(self, message):
        self.message = message

    @classmethod
    def _from_json(cls, json):
        return cls(message=json)

    def to_json(self):
        return {}

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return u'{0}'.format(self.message)


class Errors(ModelBase):

    __slots__ = ('errors',)

    FIELD_NAME = "errors"

    def __init__(self, errors):
        """
        :type errors: dict[str, Error]
        """
        self.errors = errors or {}

    def __len__(self):
        return len(self.errors)

    def to_json(self):
        return {'erorrs': ['mock']}

    @classmethod
    def _from_json(cls, json):
        errors = {
            field: map(Error.from_json, to_iter(errors))
            for field, errors in json.iteritems()
        }
        return cls(errors)

    def get_errors_for_field(self, field_name):
        """
        :type field_name: str
        :rtype: list[Error]
        """
        return self.errors.get(field_name, [])

    def __str__(self):
        return 'Errors: {0}' + '; '.join(["{0}: {1}".format(k, ','.join(v)) for k, v in self.errors])
