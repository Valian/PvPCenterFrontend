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


class GameRuleEntry(ModelBase):

    __slots__ = ('key', 'value')

    def __init__(self, key, value):
        self.key = key
        self.value = value

    @classmethod
    def _from_json(cls, json):
        return cls(json['key'], json['value'])

    def __str__(self):
        return '{0} - {1}'.format(self.key, self.value)

    def to_json(self):
        return {'key': self.key, 'value': self.value}


class GameRule(ModelBase):

    __slots__ = ('name', 'entries')

    def __init__(self, name, entries):
        self.name = name
        self.entries = entries

    @classmethod
    def _from_json(cls, json):
        entries = map(GameRuleEntry.from_json, json['entries'])
        return cls(json['name'], entries)

    def __str__(self):
        return 'Rule {0}: {1}'.format(self.name, ', '.join(map(str, self.entries)))

    def to_json(self):
        entries_json = map(GameRuleEntry.to_json, self.entries)
        return {'name': self.name, 'entries': entries_json}


class Game(ModelBase):

    __slots__ = ('id', 'name')

    def __init__(self, id, name, rules):
        self.id = id
        self.name = name
        self.rules = rules

    @classmethod
    def _from_json(cls, json):
        rules = map(GameRule.from_json, json.get('rules', []))
        return cls(json['id'], json['name'], rules)

    def to_json(self):
        rules = map(GameRule.to_json, self.rules)
        return {'id': self.id, 'name': self.name, 'rules': rules}

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

    def __init__(self, id, name, email, token, ranking, nationality, sex, age, description, game_ownerships):
        self.ranking = ranking
        self.id = id
        self.name = name
        self.email = email
        self.token = token
        self.game_ownerships = game_ownerships
        self.description = description
        self.age = age
        self.sex = sex
        self.nationality = nationality

    @classmethod
    def _from_json(cls, json):
        game_ownerships = [UserGameOwnership.from_json(go) for go in json.get('game_ownerships', [])]
        return cls(
            id=json['id'],
            name=json['nickname'],
            email=json['email'],
            token=json.get('access_token'),
            ranking=json['ranking'],
            nationality=json.get('country'),
            sex=json.get('sex'),
            age=json.get('age'),
            description=json.get('description'),
            game_ownerships=game_ownerships)

    def to_json(self):
        game_ownerships = [go.to_json() for go in self.game_ownerships]
        return {
            'id': self.id,
            'nickname': self.name,
            'email': self.email,
            'access_token': self.token,
            'game_ownerships': game_ownerships,
            'country': self.nationality,
            'sex': self.sex,
            'age': self.age,
            'description': self.description,
            'ranking': self.ranking}

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
