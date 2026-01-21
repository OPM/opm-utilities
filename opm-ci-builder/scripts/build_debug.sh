#!/bin/bash

set -e

# Build boost
git clone --depth 1 --branch boost-1.84.0 https://github.com/boostorg/boost
pushd boost
git submodule init
git submodule update
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug \
         -DCMAKE_CXX_FLAGS_INIT="-D_GLIBCXX_DEBUG"\
         -DCMAKE_C_COMPILER=/usr/lib/ccache/gcc \
         -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
         -DCMAKE_INSTALL_PREFIX=/debug_iter \
         -DBUILD_SHARED_LIBS=1 \
         -GNinja \
         -DBOOST_EXCLUDE_LIBRARIES=numeric/odeint
ninja install
popd

# Build vexcl
git clone --depth 1 --branch 1.4.3 https://github.com/ddemidov/vexcl
mkdir -p vexcl/build
pushd vexcl/build
cmake .. -DCMAKE_BUILD_TYPE=Debug \
         -DCMAKE_C_COMPILER=/usr/lib/ccache/gcc \
         -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
         -DCMAKE_CXX_FLAGS_INIT="-D_GLIBCXX_DEBUG"\
         -DCMAKE_INSTALL_PREFIX=/debug_iter \
         -GNinja
ninja install
popd

# Build amgcl
git clone --depth 1 --branch 1.4.2 https://github.com/ddemidov/amgcl
mkdir -p amgcl/build
pushd amgcl/build
cmake .. -DCMAKE_BUILD_TYPE=Debug \
         -DCMAKE_C_COMPILER=/usr/lib/ccache/gcc \
         -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
         -DCMAKE_CXX_FLAGS_INIT="-D_GLIBCXX_DEBUG"\
         -DCMAKE_INSTALL_PREFIX=/debug_iter \
         -GNinja
ninja install
popd

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
  mkdir -p $repo/build_debug
  cd $repo/build_debug
  cmake .. -GNinja \
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
           -DCMAKE_DISABLE_FIND_PACKAGE_Doxygen=1
  ninja install
  cd ../..
done

# Build damaris
mkdir -p damaris/build_debug
cd damaris/build_debug
CC=/usr/lib/ccache/gcc CXX=/usr/lib/ccache/g++ \
cmake .. -GNinja -DCMAKE_C_COMPILER=/usr/bin/mpicc \
                 -DCMAKE_CXX_COMPILER=/usr/bin/mpicxx \
                 -DCMAKE_BUILD_TYPE=Debug \
                 -DCMAKE_CXX_FLAGS_INIT="-D_GLIBCXX_DEBUG"\
                 -DBUILD_SHARED_LIBS=OFF \
                 -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
                 -DHDF5_PREFER_PARALLEL=ON \
                 -DENABLE_HDF5=ON \
                 -DCMAKE_PREFIX_PATH=/debug_iter \
                 -DCMAKE_INSTALL_PREFIX=/debug_iter
ninja install

# Build fmt
git clone --depth 1 --branch 9.1.0 https://github.com/fmtlib/fmt
mkdir -p fmt/build_debug
cd fmt/build_debug
cmake .. -DCMAKE_BUILD_TYPE=Debug \
         -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
         -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
         -DCMAKE_CXX_FLAGS_INIT="-D_GLIBCXX_DEBUG"\
         -DCMAKE_INSTALL_PREFIX=/debug_iter \
         -GNinja
ninja install

cd /debug_iter
patch -p0 < /tmp/opm/patches/dune-common/0001-gpu_patch.patch
patch -p0 < /tmp/opm/patches/dune-istl/0001-missing_initializers.patch
patch -p0 < /tmp/opm/patches/dune-fem/0002-missing_include.patch
