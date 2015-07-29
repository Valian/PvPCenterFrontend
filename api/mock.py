# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import random

import sys
import inspect

import factory
import factory.fuzzy as fuzzy
import re
from faker import Factory as FakerFactory

from models import User, Game, ModelList, UserGameOwnership
from api import ApiDispatcherBase, ApiResult


faker = FakerFactory.create()


def create_mock_for(model, list_count=5, **kwargs):
    if isinstance(model, ModelList.For):
        underlying_model = model.model
        fac = find_factory_in_inheritance_chain(underlying_model)
        data = [underlying_model.from_json(fac(**kwargs).to_json()) for _ in xrange(list_count)]
        return ModelList(data, len(data))
    fac = find_factory_in_inheritance_chain(model)
    return model.from_json(fac(**kwargs).to_json())


def find_factory_in_inheritance_chain(model):
        for cls in model.__mro__:
            if cls in factories_by_model:
                return factories_by_model[cls]
        raise NotImplemented("Create factory for {0} first".format(model))


class ApiDispatcherMock(ApiDispatcherBase):

    def make_request(self, method, endpoint, model, **kwargs):
        params = self.find_props(endpoint)
        return ApiResult(data=create_mock_for(model, **params))

    @staticmethod
    def find_props(url):
        obj_id = re.match(r'.*(\d+)$', url)
        params = {}
        if obj_id:
            params['id'] = int(obj_id.group(1))
        return params


class GameFactory(factory.Factory):
    class Meta:
        model = Game

    id = factory.Sequence(lambda x: x)
    name = factory.LazyAttribute(lambda x: faker.word())


class UserGameOwnershipFactory(factory.Factory):
    class Meta:
        model = UserGameOwnership

    id = factory.Sequence(lambda x: x)
    nickname = factory.LazyAttribute(
        lambda x: random_with_seed(faker.provider('faker.providers.person').first_names, x.id))
    game = factory.SubFactory(GameFactory)


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda x: x)
    name = factory.LazyAttribute(lambda x: random_with_seed(faker.provider('faker.providers.person').first_names, x.id))
    email = factory.LazyAttribute(lambda o: '{0}@mock.com'.format(o.name.replace(' ', '_')))
    token = fuzzy.FuzzyText(length=15)
    game_ownerships = factory.List([factory.SubFactory(UserGameOwnershipFactory) for _ in xrange(random.randint(2, 5))])


def random_with_seed(array, seed):
    return array[(seed * 34 + 391) % len(array)]


def find_classes():
    return map(lambda x: x[1], inspect.getmembers(sys.modules[__name__], inspect.isclass))

factories_by_model = {cls._meta.model: cls for cls in find_classes() if issubclass(cls, factory.Factory)}








