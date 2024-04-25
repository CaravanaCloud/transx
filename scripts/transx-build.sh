#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SOURCE_DIR="$(dirname $SCRIPT_DIR)"

TRANSX_DIR="$SOURCE_DIR/transx"
pushd $TRANSX_DIR
poetry build
popd