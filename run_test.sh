#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

for PYTHON in python2 python3 ; do
    echo ------------------------------------------------
    echo Testing with $PYTHON...
    $PYTHON "$SCRIPT_DIR/setup.py" test
done
