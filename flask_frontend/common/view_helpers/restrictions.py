# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask_login


class RestrictionRegistry(object):

    available_registers = {}

    @classmethod
    def register(cls, name):
        def add_to_register(f):
            cls.available_registers[name] = f
            return f
        return add_to_register

    @classmethod
    def get_restrictions_statuses(cls, restrictions, env, kwargs):
        try:
            return {
                name: cls.available_registers[name](env, kwargs)
                for name in restrictions}
        except KeyError as e:
            raise NotImplementedError('You have to implement {0} restriction'.format(e))

    @classmethod
    def can_proceed(cls, restrictions, env, kwargs):
        return all((
            cls.available_registers[name](env, kwargs)
            for name in restrictions))

@RestrictionRegistry.register('logged_in')
def only_logged_in(env, kwargs):
    return flask_login.current_user.is_authenticated()