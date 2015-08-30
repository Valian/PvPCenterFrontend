# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
from flask_frontend.config.common import CommonConfig


def get_local_config(config=None):
    try:
        from flask_frontend.config.local import LocalConfig
    except ImportError:
        LocalConfig = {}
    from flask_frontend.config.dev import DevConfig
    return _create_config(CommonConfig, DevConfig, LocalConfig, config)


def get_production_config(config=None):
    from flask_frontend.config.production import ProductionConfig
    return _create_config(CommonConfig, ProductionConfig, config)


def get_test_config(config=None):
    from flask_frontend.config.test import TestConfig
    return _create_config(CommonConfig, TestConfig, config)


def _create_config(*args):
    conf = dict(args[0]) if len(args) > 0 else {}
    for i in xrange(1, len(args)):
        conf.update(args[i] or {})
    return conf
