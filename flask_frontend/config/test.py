# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask_frontend.config import keys

TestConfig = {
    keys.TESTING: True,
    "WTF_CSRF_ENABLED": False,
    keys.MOCK_API: True
}
