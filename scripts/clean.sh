#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SOURCE_DIR="$(dirname $SCRIPT_DIR)"
DATA_DIR=$SOURCE_DIR/transx/sample-data/

# delete all .srt .vtt and .jsonfiles in sample-data folder 
rm -f $DATA_DIR/*.srt
rm -f $DATA_DIR/*.vtt
rm -f $DATA_DIR/*.json

