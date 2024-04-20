#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SOURCE_DIR="$(dirname $SCRIPT_DIR)"

cd $SOURCE_DIR/transx_web 
poetry run python manage.py migrate
poetry run python manage.py runserver

