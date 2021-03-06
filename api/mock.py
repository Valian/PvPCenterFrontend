# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import random
import sys
import inspect
import datetime
import logging

import factory
import factory.fuzzy as fuzzy
import re
from faker import Factory as FakerFactory

from .core import ApiResult, ApiDispatcherBase
from constants import RELATION_TO_CURRENT_USER, TEAM_PROPOSITION_TYPE
from constants import NATIONALITIES, TEAM_RELATION_TO_CURRENT_USER
from .constants import SEX
from models import User, Game, ModelList, UserGameOwnership, GameRuleEntry, GameRule, Team, TeamMembership, \
    FriendshipInvite, Friendship, RelationToUser, DeleteResponse, Notification, TeamProposition, TeamRelationToUser, \
    ListOfModel, NotificationsList


CLOUDINARY_URL = 'http://res.cloudinary.com/dihrxuryz/image/upload/v1442074482/xmhoxjbioanmd5htrl0p.png'

faker = FakerFactory.create()
logger = logging.getLogger('factory')
logger.setLevel(logging.INFO)


def create_mock_for(model, list_count=21, **kwargs):
    if isinstance(model, ListOfModel):
        underlying_model = model.model
        underlying_list_model = model.list_class
        fac = find_factory_in_inheritance_chain(underlying_model)
        list_fac = find_factory_in_inheritance_chain(underlying_list_model)
        data = fac.create_batch(list_count, **kwargs)
        return list_fac(models=data)
    fac = find_factory_in_inheritance_chain(model)
    return fac(**kwargs)


def find_factory_in_inheritance_chain(model):
    for cls in model.__mro__:
        if cls in factories_by_model:
            return factories_by_model[cls]
    raise NotImplemented("Create factory for {0} first".format(model))


class ApiDispatcherMock(ApiDispatcherBase):

    def make_request(self, method, endpoint, model, **kwargs):
        params = self.find_props(endpoint, model)
        logging.info('Mock {0} request to {1} endpoint with params {2}'.format(method, endpoint, kwargs))
        return ApiResult(data=create_mock_for(model, **params))

    @staticmethod
    def find_props(url, model):
        method_args_names = inspect.getargspec(model.__init__)
        params = {}
        for name in method_args_names[0]:
            if 'id' not in name:
                continue
            obj_id = re.match(r'.*/(\d+)', url)
            if obj_id:
                params['id'] = int(obj_id.group(1))
        return params


class ModelListFactory(factory.Factory):
    class Meta:
        model = ModelList

    models = []
    total = factory.lazy_attribute(lambda o: len(o.models) * 3)


class NotificationsListFactory(factory.Factory):
    class Meta:
        model = NotificationsList

    models = []
    total = factory.lazy_attribute(lambda o: len(o.models) * 3)
    unread_count = factory.lazy_attribute(lambda o: len(o.models) / 2)


class GameRuleEntryFactory(factory.Factory):
    class Meta:
        model = GameRuleEntry

    key = factory.fuzzy.FuzzyChoice(['Main rule', 'Secondary rule', 'Fucking rule', 'Undefined', 'Krystiansoon'])
    value = factory.Iterator(['Blah', 'Bleh', 'Shiet'])


class GameRuleFactory(factory.Factory):
    class Meta:
        model = GameRule

    name = factory.Iterator(['Basic info', 'Gamer experience', 'Allowed map', 'Special'])
    entries = factory.List([factory.SubFactory(GameRuleEntryFactory) for _ in xrange(3)])


class GameFactory(factory.Factory):
    class Meta:
        model = Game

    id = factory.Iterator([1, 2, 3, 4, 5])
    name = factory.LazyAttribute(lambda o: ['League of Legends', 'Dota', 'CS:GO', 'Minecraft', 'Worms'][o.id % 5])
    rules = factory.List([factory.SubFactory(GameRuleFactory) for _ in xrange(3)])


class UserGameOwnershipFactory(factory.Factory):
    class Meta:
        model = UserGameOwnership

    id = factory.Sequence(lambda x: x)
    nickname = factory.LazyAttribute(
        lambda x: random_with_seed(faker.provider('faker.providers.person').first_names, x.id))
    game = factory.SubFactory(GameFactory)


class DeleteResponseFactory(factory.Factory):
    class Meta:
        model = DeleteResponse

    success = True


class RelationToUserFactory(factory.Factory):
    class Meta:
        model = RelationToUser

    type = factory.Iterator(vars(RELATION_TO_CURRENT_USER).values())


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda x: x)
    name = factory.LazyAttribute(lambda x: random_with_seed(faker.provider('faker.providers.person').first_names, x.id))
    email = factory.LazyAttribute(lambda o: '{0}@mock.com'.format(o.name.replace(' ', '_')))
    token = fuzzy.FuzzyText(length=15)
    nationality = factory.LazyAttribute(lambda o: NATIONALITIES.CODE_TO_NATIONALITY.keys()[o.id % len(NATIONALITIES.CODES)])
    sex = factory.LazyAttribute(lambda o: [SEX.UNDEFINED, SEX.MALE, SEX.FEMALE][o.id % 3])
    birthdate = factory.LazyAttribute(lambda o: datetime.date(1992, 12, 03))
    description = factory.LazyAttribute(lambda o: [None, 'Taki oto ja', 'Pro elo elo'][o.id % 3])
    ranking = factory.LazyAttribute(lambda o: (o.id * 13 + 7) % 100 + 30)
    game_ownerships = factory.List([factory.SubFactory(UserGameOwnershipFactory) for _ in xrange(random.randint(2, 5))])
    relation_to_current_user = factory.SubFactory(RelationToUserFactory)
    image_url = factory.LazyAttribute(lambda o: [None, CLOUDINARY_URL][o.id % 2])


class TeamRelationToUserFactory(factory.Factory):
    class Meta:
        model = TeamRelationToUser

    type = factory.Iterator(vars(TEAM_RELATION_TO_CURRENT_USER).values())


class TeamFactory(factory.Factory):
    class Meta:
        model = Team

    id = factory.Sequence(lambda x: x)
    name = factory.LazyAttribute(lambda x: random_with_seed(faker.provider('faker.providers.lorem').word_list, x.id))
    description = factory.LazyAttribute(lambda o: [None, 'Taki oto ja', 'Pro elo elo'][o.id % 3])
    tag = factory.LazyAttribute(lambda o: ['HEY', 'ELO', 'WIN'][o.id % 3])
    founder = factory.SubFactory(UserFactory)
    member_count = factory.LazyAttribute(lambda o: o.id * 17 % 10 + 5)
    relation_to_current_user = factory.SubFactory(TeamRelationToUserFactory)
    image_url = factory.LazyAttribute(lambda o: [None, CLOUDINARY_URL][o.id % 2])


class TeamMembershipFactory(factory.Factory):
    class Meta:
        model = TeamMembership

    id = factory.Sequence(lambda x: x)
    user = factory.SubFactory(UserFactory)
    team = factory.SubFactory(TeamFactory)


class TeamPropositionFactory(factory.Factory):
    class Meta:
        model = TeamProposition

    id = factory.Sequence(lambda x: x)
    team = factory.SubFactory(TeamFactory)
    user = factory.SubFactory(UserFactory)
    type = factory.Iterator(vars(TEAM_PROPOSITION_TYPE).values())


class FriendshipInviteFactory(factory.Factory):
    class Meta:
        model = FriendshipInvite

    id = factory.Sequence(lambda x: x)
    from_user = factory.SubFactory(UserFactory)
    to_user = factory.SubFactory(UserFactory)


class FriendshipFactory(factory.Factory):
    class Meta:
        model = Friendship

    id = factory.Sequence(lambda x: x)
    friend = factory.SubFactory(UserFactory)


class NotificationFactory(factory.Factory):
    class Meta:
        model = Notification

    id = factory.Sequence(lambda x: x)
    user_id = factory.Sequence(lambda x: x)
    content = faker.text()
    notification_type = factory.Iterator(["Info", "Event", "Unknown"])
    creation_time = factory.LazyAttribute(lambda o: datetime.datetime.utcnow() - datetime.timedelta(minutes=random.randint(5, 500)))
    checked = factory.Iterator([True, False])


def random_with_seed(array, seed):
    return array[(seed * 34 + 391) % len(array)]


def find_classes():
    return map(lambda x: x[1], inspect.getmembers(sys.modules[__name__], inspect.isclass))

factories_by_model = {cls._meta.model: cls for cls in find_classes() if issubclass(cls, factory.Factory)}








