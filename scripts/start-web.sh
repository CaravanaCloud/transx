#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SOURCE_DIR="$(dirname $SCRIPT_DIR)"

TRANSX_WEB_DIR="$SOURCE_DIR/transx_web" 
pushd $TRANSX_WEB_DIR
poetry install
poetry run python manage.py runserver
popd


