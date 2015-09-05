# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import flask


class FLASH_TYPES(object):
    ERROR = 'error'
    SUCCESS = 'success'
    INFO = 'info'
    WARNING = 'warning'


class Flash(object):

    @staticmethod
    def success(message):
        flask.flash(message, FLASH_TYPES.SUCCESS)

    @staticmethod
    def error(message):
        flask.flash(message, FLASH_TYPES.ERROR)

    @staticmethod
    def info(message):
        flask.flash(message, FLASH_TYPES.INFO)

    @staticmethod
    def warning(message):
        flask.flash(message, FLASH_TYPES.WARNING)
