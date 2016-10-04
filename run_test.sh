#!/bin/bash
set -e
cd "$(dirname "$0")"
PYTHONPATH=$(pwd)
export PYTHONPATH

if [ $TRAVIS ] ; then
    PYTHON_VERSIONS=python
else
    PYTHON_VERSIONS='python2 python3'
fi

for PYTHON in $PYTHON_VERSIONS ; do
    $PYTHON -m flake8 exrsplit/
    $PYTHON -m pytest "$@"  # additional options are passed to pytest
done
