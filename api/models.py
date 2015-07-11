# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from abc import ABCMeta, abstractmethod
from common.utils import abstractstaticmethod, to_iter


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

    @abstractstaticmethod
    def _from_json(json):
        raise NotImplementedError

    @abstractmethod
    def __str__(self):
        return super(ModelBase, self).__str__()


class ModelList(object):

    def __init__(self, data, total):
        self.data = data
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

    @staticmethod
    def _from_json(json):
        return Game(json['id'], json['name'])

    def __str__(self):
        return '[Game {0}:{1}]'.format(self.id, self.name)


class User(ModelBase):

    def __init__(self, id, name, email, token):
        self.id = id
        self.name = name
        self.email = email
        self.token = token

    @staticmethod
    def _from_json(json):
        return User(json['id'], json['nickname'], json['email'], json.get('access_token'))

    def __str__(self):
        return '[User {0}: {1} - {2}]'.format(self.id, self.name, self.email)


class Error(ModelBase):

    __slots__ = ('message',)

    def __init__(self, message):
        self.message = message

    @staticmethod
    def _from_json(json):
        return Error(message=json)

    def __str__(self):
        return '[Error: {0}]'.format(self.message)


class Errors(ModelBase):

    __slots__ = ('errors',)

    FIELD_NAME = "errors"

    def __init__(self, errors):
        """
        :type errors: dict[Error]
        """
        self.errors = errors or {}

    @staticmethod
    def _from_json(json):
        errors = {
            field: map(Error.from_json, to_iter(errors))
            for field, errors in json.iteritems()
        }
        return Errors(errors)

    def get_errors_for_field(self, field_name):
        """
        :type field_name: str
        :rtype: list[Error]
        """
        return self.errors.get(field_name, [])

    def __str__(self):
        return 'Errors: {0}' + '; '.join(["{0}: {1}".format(k, ','.join(v)) for k, v in self.errors])
