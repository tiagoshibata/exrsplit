#!/bin/bash
set -e
cd "$(dirname "$0")"

python2 -m flake8 --max-line-length=120 --max-complexity=10 exrsplit/
python2 -m pytest --cov=exrsplit/ --cov-config=.coveragerc --cov-report=term --cov-report=html tests/ "$@"
