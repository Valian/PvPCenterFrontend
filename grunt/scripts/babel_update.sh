#!/bin/bash

LANGUAGE="$1"
ROOT=$(git rev-parse --show-toplevel)

if [ -z "$LANGUAGE" ]; then
    echo "Usage: babel_init.sh LOCALE, eg. babel_init.sh pl"
    exit 1
fi

if [ -d "$ROOT/flask_frontend/translations/$LANGUAGE" ]; then
    echo "Translation exists, use update script instead."
    exit 2
fi

mkdir $ROOT/flask_frontend/translations

echo "extracting strings..."
pybabel extract -F $ROOT/flask_frontend/config/babel.cfg -o $ROOT/flask_frontend/translations/messages.pot $ROOT/flask_frontend

if [ $? -ne 0 ]; then
    echo "error, aborting"
    exit 3
fi

echo "creating translation..."
pybabel init -i $ROOT/flask_frontend/translations/messages.pot -d $ROOT/flask_frontend/translations -l $LANGUAGE

if [ $? -ne 0 ]; then
    echo "error, aborting"
    exit 4
fi

echo "done."
