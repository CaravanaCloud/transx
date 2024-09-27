SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SOURCE_DIR="$(dirname $SCRIPT_DIR)"

cd $SOURCE_DIR/transx-api
poetry install
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload