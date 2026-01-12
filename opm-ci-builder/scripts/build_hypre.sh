#!/bin/bash

set -e

git clone https://github.com/hypre-space/hypre
cd hypre
git checkout $1
mkdir -p src/build
cd src/build
cmake .. -GNinja -DCMAKE_C_COMPILER=/usr/lib/ccache/gcc \
                 -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
                 -DBUILD_SHARED_LIBS=0 \
                 -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
                 -DCMAKE_CXX_STANDARD=17 \
                 -DCMAKE_INSTALL_PREFIX=/hypre/cpu \
                 -DHYPRE_BUILD_EXAMPLES=OFF \
                 -DHYPRE_BUILD_TESTS=OFF \
                 -DHYPRE_ENABLE_UMPIRE=OFF
ninja install
cd ../..

mkdir -p src/build_cuda

cd src/build_cuda
cmake .. -GNinja -DCMAKE_C_COMPILER=/usr/lib/ccache/gcc \
                 -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
                 -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc \
                 -DCMAKE_CUDA_ARCHITECTURES=80 \
                 -DBUILD_SHARED_LIBS=0 \
                 -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
                 -DCMAKE_CXX_STANDARD=17 \
                 -DCMAKE_CUDA_STANDARD=17 \
                 -DCMAKE_INSTALL_PREFIX=/hypre/cuda \
                 -DCUDA_PATH=/usr/local/cuda \
                 -DHYPRE_ENABLE_CUDA=ON \
                 -DHYPRE_BUILD_EXAMPLES=OFF \
                 -DHYPRE_BUILD_TESTS=OFF \
                 -DHYPRE_ENABLE_UMPIRE=OFF
ninja install
cd ../..


patch -p1 < /tmp/opm/patches/hypre/0001-fix_hip_build.patch
mkdir -p src/build_hip

cd src/build_hip
cmake .. -GNinja -DCMAKE_C_COMPILER=/usr/lib/ccache/gcc \
                 -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
                 -DCMAKE_HIP_ARCHITECTURES=gfx942 \
                 -DGPU_TARGETS=gfx942 \
                 -DBUILD_SHARED_LIBS=0 \
                 -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
                 -DCMAKE_CXX_STANDARD=17 \
                 -DCMAKE_HIP_STANDARD=17 \
                 -DCMAKE_INSTALL_PREFIX=/hypre/hip \
                 -DHYPRE_ENABLE_HIP=ON \
                 -DHYPRE_BUILD_EXAMPLES=OFF \
                 -DHYPRE_BUILD_TESTS=OFF \
                 -DHYPRE_ENABLE_UMPIRE=OFF

ninja install
cd ../../..
