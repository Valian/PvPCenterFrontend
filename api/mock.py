# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import random

import sys
import inspect
import factory
import factory.fuzzy as fuzzy

from faker import Factory as FakerFactory
from models import User, Game, ModelList
from api import ApiDispatcherBase, ApiResult

faker = FakerFactory.create()


class ApiDispatcherMock(ApiDispatcherBase):

    def make_request(self, method, endpoint, model, **kwargs):
        return self.create_mock_for(model)

    @staticmethod
    def create_mock_for(model):
        if isinstance(model, ModelList.For):
            fac = ApiDispatcherMock.find_factory_in_inheritance_chain(model.model)
            data = [model.from_json(fac().to_json()) for _ in xrange(random.randint(3, 6))]
            return ApiResult(data=ModelList(data, len(data)))
        fac = ApiDispatcherMock.find_factory_in_inheritance_chain(model)
        return ApiResult(data=model.from_json(fac().to_json()))

    @staticmethod
    def find_factory_in_inheritance_chain(model):
        for cls in model.__mro__:
            if cls in factories_by_model:
                return factories_by_model[cls]
        raise NotImplemented("Create factory for {0} first".format(model))


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda x: x)
    name = factory.LazyAttribute(lambda x: faker.last_name())
    email = factory.LazyAttribute(lambda o: '{0}@mock.com'.format(o.name.replace(' ', '_')))
    token = fuzzy.FuzzyText(length=15)


class GameFactory(factory.Factory):
    class Meta:
        model = Game

    id = factory.Sequence(lambda x: x)
    name = factory.LazyAttribute(lambda x: faker.word())


def find_classes():
    return map(lambda x: x[1], inspect.getmembers(sys.modules[__name__], inspect.isclass))

factories_by_model = {cls._meta.model: cls for cls in find_classes() if issubclass(cls, factory.Factory)}








