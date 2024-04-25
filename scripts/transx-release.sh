#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SOURCE_DIR="$(dirname $SCRIPT_DIR)"

VERSION_XY=$(cat $SOURCE_DIR/version.txt)
VERSION_Z=$(date +%s)
VERSION_XYZ="${VERSION_XY}.${VERSION_Z}"

echo "Building [transx] $VERSION_XYZ"
source "$SCRIPT_DIR/transx-build.sh"

echo "Releasing $VERSION_XYZ [cli module]"
