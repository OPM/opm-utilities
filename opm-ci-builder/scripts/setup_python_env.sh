#!/bin/bash

set -e

python3 -m virtualenv /python_env
source /python_env/bin/activate

python3 -m pip install pybind11 numpy decorator jinja2 lxml matplotlib scipy filelock
