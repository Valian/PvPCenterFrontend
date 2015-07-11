# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from abc import ABCMeta, abstractmethod
from common.abstractutils import abstractstaticmethod


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


class Error(ModelBase):

    __slots__ = ('message',)

    def __init__(self, message):
        self.message = message

    @staticmethod
    def _from_json(json):
        return Error(message=json)

    def __str__(self):
        return '[Error {0}]'.format(self.message)


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
            field: map(Error.from_json, errors)
            for field, errors in json.get(Errors.FIELD_NAME, {}).iteritems()
        }
        return Errors(errors)

    def get_errors_for_field(self, field_name):
        """
        :type field_name: str
        :rtype: list[Error]
        """
        return self.errors.get(field_name, [])

    def __str__(self):
        return 'Errors' + ','.join(self.errors)



