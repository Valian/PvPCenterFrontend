# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

import os

from flask_frontend.config import keys

ProductionConfig = {
    keys.BACKEND_URL: 'http://{address}:3000'.format(address=os.environ["CORE_PORT_3000_TCP_ADDR"]),
    keys.BACKEND_LOGIN: os.environ["CORE_ENV_CORE_LOGIN"],
    keys.BACKEND_PASS: os.environ["CORE_ENV_CORE_PASSWORD"],

    keys.CLOUDINARY_CLOUD_NAME: os.environ["CLOUDINARY_CLOUD_NAME"],
    keys.CLOUDINARY_SECRET: os.environ["CLOUDINARY_SECRET"],
    keys.CLOUDINARY_PUBLIC_KEY: os.environ["CLOUDINARY_PUBLIC_KEY"],
}
