#!/bin/bash

ROOT=$(git rev-parse --show-toplevel)

if [ ! -d "$ROOT/flask_frontend/translations" ]; then
    echo "No translations exists. Use babel_init.sh first."
    exit 1
fi

echo "compiling..."
pybabel compile -d $ROOT/flask_frontend/translations

if [ $? -ne 0 ]; then
    echo "error, aborting"
    exit 2
fi

echo "done."
