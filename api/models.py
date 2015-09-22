# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from abc import ABCMeta

from constants import RELATION_TO_CURRENT_USER, TEAM_RELATION_TO_CURRENT_USER as TEAM_RELATION
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
        except Exception as e:
            raise UnableToParseException(cls, e)

    @abstractclassmethod
    def _from_json(cls, json):
        raise NotImplementedError()

    def __str__(self):
        return str(vars(self))


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


class GameRule(ModelBase):
    __slots__ = ('name', 'entries')

    def __init__(self, name, entries):
        self.name = name
        self.entries = entries

    @classmethod
    def _from_json(cls, json):
        entries = map(GameRuleEntry.from_json, json['entries'])
        return cls(json['name'], entries)


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


class UserGameOwnership(ModelBase):
    def __init__(self, id, nickname, game):
        self.id = id
        self.nickname = nickname
        self.game = game

    @classmethod
    def _from_json(cls, json):
        game = Game.from_json(json['game'])
        return cls(json['id'], json.get('nickname'), game)


class DeleteResponse(ModelBase):

    def __init__(self, success):
        self.success = success

    @classmethod
    def _from_json(cls, json):
        return cls(json.get('success', True))


class RelationToUser(ModelBase):

    def __init__(self, type):
        """
        :type type: str
        """
        self.type = type

    @classmethod
    def _from_json(cls, json):
        return cls(json)

    @property
    def is_friend(self):
        return self.type == RELATION_TO_CURRENT_USER.FRIEND

    @property
    def invite_send(self):
        return self.type == RELATION_TO_CURRENT_USER.SEND_INVITE

    @property
    def invite_received(self):
        return self.type == RELATION_TO_CURRENT_USER.RECEIVED_INVITE


class User(ModelBase):

    def __init__(self, id, name, email, token, ranking, nationality, sex, birthdate, description, game_ownerships,
                 relation_to_current_user, image_url):
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
        self.image_url = image_url

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
            nationality=json.get('nationality'),
            sex=json.get('sex'),
            relation_to_current_user=relation,
            birthdate=json.get('birthdate'),
            description=json.get('description'),
            image_url=json.get('image_url'),
            game_ownerships=game_ownerships)
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class Friendship(ModelBase):

    def __init__(self, id, friend):
        self.id = id
        self.friend = friend

    @classmethod
    def _from_json(cls, json):
        friend = User.from_json(json['friend'])
        return cls(json['id'], friend)


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


class Division(ModelBase):
    def __init__(self, id, team, game):
        self.id = id
        self.team = team
        self.game = game

    @classmethod
    def _from_json(cls, json):
        raise NotImplementedError()


class TeamRelationToUser(ModelBase):

    def __init__(self, type):
        """
        :type type: TEAM_RELATION
        """
        self.type = type

    @property
    def is_founder(self):
        return self.type == TEAM_RELATION.FOUNDER

    @property
    def is_captain(self):
        return self.type in (TEAM_RELATION.FOUNDER, TEAM_RELATION.CAPTAIN)

    @property
    def is_member(self):
        return self.type in (TEAM_RELATION.MEMBER, TEAM_RELATION.FOUNDER, TEAM_RELATION.CAPTAIN)

    @property
    def is_invited(self):
        return self.type == TEAM_RELATION.INVITED

    @property
    def is_proposed(self):
        return self.type == TEAM_RELATION.PROPOSED

    @classmethod
    def _from_json(cls, json):
        return cls(json)


class Team(ModelBase):
    def __init__(self, id, name, description, tag, founder, image_url, relation_to_current_user, member_count):
        """
        :type id: long
        :type name: str
        :type description: str
        :type tag: str
        :type founder: User
        :type image_url: str
        :type relation_to_current_user: TeamRelationToUser
        :type member_count: int
        """
        self.id = id
        self.name = name
        self.description = description
        self.tag = tag
        self.founder = founder
        self.image_url = image_url
        self.member_count = member_count
        self.relation_to_current_user = relation_to_current_user

    @classmethod
    def _from_json(cls, json):
        founder = User.from_json(json['founder']) if 'founder' in json else None
        relation = TeamRelationToUser.from_json(
            json.get('current_user_relation', TEAM_RELATION.STRANGER))
        return cls(
            id=json['id'],
            name=json['name'],
            description=json.get('description'),
            tag=json.get('tag'),
            founder=founder,
            image_url=json.get('image_url'),
            relation_to_current_user=relation,
            member_count=json['member_count'])


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


class TeamInvite(ModelBase):

    def __init__(self, id, team_id, from_user=None, to_user=None):
        """
        :type id: long
        :type team_id: long
        :type from_user: long | None
        :type to_user: long | None
        """
        self.id = id
        self.team_id = team_id
        self.from_user = from_user
        self.to_user = to_user

    @classmethod
    def _from_json(cls, json):
        return cls(json['id'], json['team_id'], json.get('from_user'), json.get('to_user'))


class Notification(ModelBase):

    def __init__(self, title, content, notification_type, time, checked):
        """
        :type title: str
        :type content: str
        :type notification_type: str
        :type time: datetime
        :type checked: bool
        """
        self.title = title
        self.content = content
        self.type = notification_type
        self.time = time
        self.checked = checked

    @classmethod
    def _from_json(cls, json):
        return cls(json['title'], json['content'], json['type'], json['time'], json['checked'])


class Error(ModelBase):
    __slots__ = ('message',)

    def __init__(self, message):
        self.message = message

    @classmethod
    def _from_json(cls, json):
        return cls(message=json)

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

    @classmethod
    def _from_json(cls, json):
        errors = {
            field: map(Error.from_json, to_iter(errors))
            for field, errors in json.iteritems()}
        return cls(errors)

    def get_errors_for_field(self, field_name):
        """
        :type field_name: str
        :rtype: list[Error]
        """
        return self.errors.get(field_name, [])
