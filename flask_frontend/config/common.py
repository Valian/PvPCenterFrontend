# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import os

from flask_frontend.config import keys

CommonConfig = {
    keys.SITE_ROOT: os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    keys.STATIC_FOLDER: 'dist',

    keys.BACKEND_URL: 'url',
    keys.BACKEND_LOGIN: 'login',
    keys.BACKEND_PASS: 'pass',

    keys.LOG_LEVEL: 'INFO',

    keys.SECRET_KEY: 'secrettttt',
    keys.MOCK_API: False,
    keys.LANGUAGES: {
        'pl': 'Polski',
        'en': 'English'
    },

    keys.CLOUDINARY_CLOUD_NAME: 'unset',
    keys.CLOUDINARY_PUBLIC_KEY: 'public_key',
    keys.CLOUDINARY_SECRET: 'secret'
}
