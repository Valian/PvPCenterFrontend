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


class DeleteResponse(ModelBase):

    def __init__(self, success):
        self.success = success

    @classmethod
    def _from_json(cls, json):
        return cls(json.get('success', True))

    def __str__(self):
        return 'delete succes: {0}'.format(self.success)

    def to_json(self):
        return {'success': self.success}


class RELATION_TO_CURRENT_USER(object):
    SEND_INVITE = 'SENT_FRIENDSHIP_INVITE'
    RECEIVED_INVITE = 'RECEIVED_FRIENDSHIP_INVITE'
    FRIEND = 'FRIEND'
    STRANGER = 'STRANGER'


class RelationToUser(ModelBase):

    def __init__(self, type, id=None):
        """
        :type type: str
        :type id: long
        """
        self.type = type
        self.id = id

    @classmethod
    def _from_json(cls, json):
        return cls(json['type'], json.get('id'))

    @property
    def is_friend(self):
        return self.type == RELATION_TO_CURRENT_USER.FRIEND

    @property
    def invite_send(self):
        return self.type == RELATION_TO_CURRENT_USER.SEND_INVITE

    @property
    def invite_received(self):
        return self.type == RELATION_TO_CURRENT_USER.RECEIVED_INVITE

    def __str__(self):
        return 'Relation {0} with id {1}'.format(self.type, self.id)

    def to_json(self):
        return {'id': self.id, 'type': self.type}


class User(ModelBase):
    def __init__(self, id, name, email, token, ranking, nationality, sex, birthdate, description, game_ownerships,
                 relation_to_current_user):
        self.ranking = ranking
        self.id = id
        self.name = name
        self.email = email
        self.token = token
        self.game_ownerships = game_ownerships
        self.description = description
        self.birthdate = birthdate
        self.sex = sex
        self.nationality = nationality
        self.relation_to_current_user = relation_to_current_user

    @classmethod
    def _from_json(cls, json):
        game_ownerships = [UserGameOwnership.from_json(go) for go in json.get('game_ownerships', [])]
        relation = RelationToUser.from_json(
            json.get('relation_to_current_user', {'type': RELATION_TO_CURRENT_USER.STRANGER}))
        return cls(
            id=json['id'],
            name=json['nickname'],
            email=json['email'],
            token=json.get('access_token'),
            ranking=json.get('ranking'),
            nationality=json.get('country'),
            sex=json.get('sex'),
            relation_to_current_user=relation,
            birthdate=json.get('birthdate'),
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
            'birthdate': self.birthdate,
            'description': self.description,
            'ranking': self.ranking,
            'relation_to_current_user': self.relation_to_current_user.to_json()}

    def __str__(self):
        return '[User {0}: {1} - {2}, owned games: {3}]'.format(self.id, self.name, self.email, self.game_ownerships)


class Friendship(ModelBase):

    def __init__(self, id, friend):
        self.id = id
        self.friend = friend

    @classmethod
    def _from_json(cls, json):
        friend = User.from_json(json['friend'])
        return cls(json['id'], friend)

    def to_json(self):
        friend_json = self.friend.to_json()
        return {'id': self.id, 'friend': friend_json}

    def __str__(self):
        return 'Friendship {0} to user {1}'.format(self.id, str(self.friend))


class FriendshipInvite(ModelBase):
    def __init__(self, id, from_user, to_user):
        """
        :type id: int
        :type from_user: User
        :type to_user: User
        """
        self.id = id
        self.from_user = from_user
        self.to_user = to_user

    @classmethod
    def _from_json(cls, json):
        from_user = User.from_json(json['from_user']) if 'from_user' in json else None
        to_user = User.from_json(json['to_user']) if 'to_user' in json else None
        return cls(json['id'], from_user, to_user)

    def to_json(self):
        to_user_json = self.to_user.to_json() if self.to_user else None
        from_user_json = self.from_user.to_json() if self.from_user else None
        return {'id': self.id, 'to_user': to_user_json, 'from_user': from_user_json}

    def __str__(self):
        return 'Friendship invite from user {0} to user {1}'.format(self.from_user, self.to_user)


class Division(ModelBase):
    def __init__(self, id, team, game):
        self.id = id
        self.team = team
        self.game = game

    @classmethod
    def _from_json(cls, json):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    def to_json(self):
        raise NotImplementedError()


class Team(ModelBase):
    def __init__(self, id, name, description, tag, founder, members_count):
        """
        :type id: long
        :type name: str
        :type description: str
        :type tag: str
        :type founder: User
        :type members_count: int
        """
        self.id = id
        self.name = name
        self.description = description
        self.tag = tag
        self.founder = founder
        self.members_count = members_count

    @classmethod
    def _from_json(cls, json):
        founder = User.from_json(json['founder']) if json.has_key('founder') else None
        return cls(json['id'], json['name'], json.get('description'), json.get('tag'), founder, json['members_count'])

    def __str__(self):
        return 'Team {0}, founder {1}'.format(self.name, self.founder.name)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'tag': self.tag,
            'founder': self.founder.to_json() if self.founder else '',
            'members_count': self.members_count}


class TeamMembership(ModelBase):
    def __init__(self, id, user, team):
        """
        :type id: long
        :type user: User
        :type team: Team
        """
        self.id = id
        self.user = user
        self.team = team

    @classmethod
    def _from_json(cls, json):
        user = User.from_json(json['user'])
        team = Team.from_json(json['team'])
        return cls(json['id'], user, team)

    def __str__(self):
        return 'Membership: User {0}, Team {1}'.format(self.user.name, self.team.name)

    def to_json(self):
        return {
            'id': self.id,
            'user': self.user.to_json(),
            'team': self.team.to_json()}


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
