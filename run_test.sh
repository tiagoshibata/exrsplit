#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if python -m pytest --fixtures | grep 'xdist\.plugin' > /dev/null ; then
    PYTEST_OPTS='-n auto'
else
    echo "pytest-xdist not detected, tests won't be run in parellel"
fi

for PYTHON in python2 python3 ; do
    echo ------------------------------------------------
    echo Testing with $PYTHON...
    if [[ $PYTEST_OPTS ]] ; then
        $PYTHON "$SCRIPT_DIR/setup.py" test --addopts "$PYTEST_OPTS"
    else
        $PYTHON "$SCRIPT_DIR/setup.py" test
    fi
done
