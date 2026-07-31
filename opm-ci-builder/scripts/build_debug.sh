#!/bin/bash

set -e

# Build boost
git clone --depth 1 --branch boost-1.84.0 https://github.com/boostorg/boost
pushd boost
git submodule init
git submodule update
cmake -S . \
      -B build \
      -G Ninja \
      -DCMAKE_BUILD_TYPE=Debug \
      -DCMAKE_CXX_FLAGS_INIT="-D_GLIBCXX_DEBUG"\
      -DCMAKE_C_COMPILER=/usr/lib/ccache/gcc \
      -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
      -DCMAKE_INSTALL_PREFIX=/debug_iter \
      -DBUILD_SHARED_LIBS=ON \
      -DBOOST_EXCLUDE_LIBRARIES=numeric/odeint
cmake --build build
cmake --install build
popd

# Build vexcl
git clone --depth 1 --branch 1.4.3 https://github.com/ddemidov/vexcl
cmake -S vexcl \
      -B vexcl/build \
      -G Ninja \
      -DCMAKE_BUILD_TYPE=Debug \
      -DCMAKE_C_COMPILER=/usr/lib/ccache/gcc \
      -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
      -DCMAKE_CXX_FLAGS_INIT="-D_GLIBCXX_DEBUG"\
      -DCMAKE_INSTALL_PREFIX=/debug_iter
cmake --build vexcl/build
cmake --install vexcl/build

# Build amgcl
git clone --depth 1 --branch 1.4.2 https://github.com/ddemidov/amgcl
cmake -S amgcl \
      -B amgcl/build \
      -G Ninja \
      -DCMAKE_BUILD_TYPE=Debug \
      -DCMAKE_C_COMPILER=/usr/lib/ccache/gcc \
      -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
      -DCMAKE_CXX_FLAGS_INIT="-D_GLIBCXX_DEBUG"\
      -DCMAKE_INSTALL_PREFIX=/debug_iter
cmake --build amgcl/build
cmake --install amgcl/build

# Build dune
for repo in dune-common \
            dune-geometry \
            dune-istl \
            dune-uggrid \
            dune-grid \
            dune-localfunctions \
            dune-alugrid \
            dune-fem
do
  echo "Building $repo ${dune_version[$repo]} ${dune_repo[$repo]}"
  cmake -S $repo \
        -B $repo/build_debug \
        -G Ninja \
        -DCMAKE_BUILD_TYPE=Debug \
        -DCMAKE_DISABLE_FIND_PACKAGE_Doxygen=ON \
        -DCMAKE_CXX_FLAGS_INIT="-D_GLIBCXX_DEBUG" \
        -DCMAKE_C_COMPILER=/usr/lib/ccache/gcc \
        -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
        -DBUILD_SHARED_LIBS=OFF \
        -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
        -DDUNE_ENABLE_PYTHONBINDINGS=OFF \
        -DCMAKE_INSTALL_PREFIX=/debug_iter \
        -DCMAKE_PREFIX_PATH=/debug_iter \
        -DCMAKE_DISABLE_FIND_PACKAGE_Doxygen=ON
  cmake --build $repo/build_debug
  cmake --install $repo/build_debug
done

# Build damaris
CC=/usr/lib/ccache/gcc CXX=/usr/lib/ccache/g++ \
cmake -S damaris \
      -B damaris/build_debug \
      -G Ninja \
      -DCMAKE_C_COMPILER=/usr/bin/mpicc \
      -DCMAKE_CXX_COMPILER=/usr/bin/mpicxx \
      -DCMAKE_BUILD_TYPE=Debug \
      -DCMAKE_CXX_FLAGS_INIT="-D_GLIBCXX_DEBUG"\
      -DBUILD_SHARED_LIBS=OFF \
      -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
      -DHDF5_PREFER_PARALLEL=ON \
      -DENABLE_HDF5=ON \
      -DCMAKE_PREFIX_PATH=/debug_iter \
      -DCMAKE_INSTALL_PREFIX=/debug_iter
cmake --build damaris/build_debug
cmake --install damaris/build_debug

# Build fmt
git clone --depth 1 --branch 11.1.1 https://github.com/fmtlib/fmt
cmake -S fmt \
      -B fmt/build_debug \
      -G Ninja \
      -DCMAKE_BUILD_TYPE=Debug \
      -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
      -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
      -DCMAKE_CXX_FLAGS_INIT="-D_GLIBCXX_DEBUG"\
      -DCMAKE_INSTALL_PREFIX=/debug_iter
cmake --build fmt/build_debug
cmake --install fmt/build_debug
