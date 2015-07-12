# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import logging


class Logable(object):

    def log_debug(self, msg):
        """
        @type msg: str
        """
        logging.debug(self._prefix() + msg)

    def log_info(self, msg):
        """
        @type msg: str
        """
        logging.info(self._prefix() + msg)

    def log_warning(self, msg):
        """
        @type msg: str
        """
        logging.warning(self._prefix() + msg)

    def log_error(self, msg):
        """
        @type msg: str
        """
        logging.error(self._prefix() + msg)

    def log_critical(self, msg):
        """
        @type msg: str
        """
        logging.critical(self._prefix() + msg)

    def _prefix(self):
        """
        @rtype: str
        """
        return self.__class__.__name__ + ": "
