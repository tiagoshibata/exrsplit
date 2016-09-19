#!/bin/bash
set -e
cd "$(dirname "$0")"
PYTHONPATH=$(pwd)
export PYTHONPATH

# python2 -m flake8 exrsplit/
python2 -m pytest --cov=exrsplit/ --cov-config=.coveragerc --cov-report=term --cov-report=html tests/ "$@"
