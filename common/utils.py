# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)


def to_iter(obj):
    if hasattr(obj, '__iter__'):
        return obj
    return [obj]


class abstractstaticmethod(staticmethod):

    __slots__ = ()
    __isabstractmethod__ = True

    def __init__(self, callable):
        super(abstractstaticmethod, self).__init__(callable)
        callable.__isabstractmethod__ = True


class abstractclassmethod(classmethod):

    __slots__ = ()
    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)