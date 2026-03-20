#!/bin/bash

set -e

cd /python_env/lib/python3.12/site-packages/pybind11
patch -p1 < /tmp/opm/patches/pybind11/0001-no_static.patch

cd /usr/share/cmake-3.28/Modules/FortranCInterface
patch -p0 < /tmp/opm/patches/cmake/fix_fc_debug.patch
