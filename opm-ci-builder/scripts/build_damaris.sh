#!/bin/bash

set -e

git clone -b $1 https://gitlab.inria.fr/Damaris/damaris.git
CC=/usr/lib/ccache/gcc CXX=/usr/lib/ccache/g++ \
cmake -S damaris \
      -B damaris/build \
      -G Ninja \
      -DCMAKE_C_COMPILER=/usr/bin/mpicc \
      -DCMAKE_CXX_COMPILER=/usr/bin/mpicxx \
      -DBUILD_SHARED_LIBS=OFF \
      -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
      -DHDF5_PREFER_PARALLEL=ON \
      -DENABLE_HDF5=ON \
      -DCMAKE_INSTALL_PREFIX=/usr/local
cmake --build damaris/build
cmake --install damaris/build
