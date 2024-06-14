#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SOURCE_DIR="$(dirname $SCRIPT_DIR)"

SCRIPT_DIR="$SOURCE_DIR/scripts"
pushd $SCRIPT_DIR
source start-web.sh

popd
