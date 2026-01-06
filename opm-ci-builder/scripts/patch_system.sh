#!/bin/bash

set -e

cd /usr/include
patch -p1 < /tmp/opm/patches/dune-common/0001-gpu_patch.patch
patch -p1 < /tmp/opm/patches/dune-istl/0001-missing_initializers.patch
patch -p1 < /tmp/opm/patches/dune-fem/0002-missing_include.patch

cd /dune/serial
patch -p0 < /tmp/opm/patches/dune-common/0001-gpu_patch.patch
patch -p0 < /tmp/opm/patches/dune-istl/0001-missing_initializers.patch
patch -p0 < /tmp/opm/patches/dune-fem/0002-missing_include.patch
