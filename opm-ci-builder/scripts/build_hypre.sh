#!/bin/bash

set -e

git clone https://github.com/hypre-space/hypre
git -C hypre checkout $1
patch -d hypre -p1 < /tmp/opm/patches/hypre/fix_finalize.patch
cmake -S hypre/src \
      -B hypre/src/build \
      -G Ninja \
      -DCMAKE_C_COMPILER=/usr/lib/ccache/gcc \
      -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
      -DBUILD_SHARED_LIBS=0 \
      -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
      -DCMAKE_CXX_STANDARD=20 \
      -DCMAKE_INSTALL_PREFIX=/hypre/cpu \
      -DHYPRE_BUILD_EXAMPLES=OFF \
      -DHYPRE_BUILD_TESTS=OFF \
      -DHYPRE_ENABLE_UMPIRE=OFF
cmake --build hypre/src/build
cmake --install hypre/src/build

cmake -S hypre/src \
      -B hypre/src/build_cuda \
      -G Ninja \
      -DCMAKE_C_COMPILER=/usr/lib/ccache/gcc \
      -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
      -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc \
      -DCMAKE_CUDA_ARCHITECTURES=80 \
      -DBUILD_SHARED_LIBS=0 \
      -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
      -DCMAKE_CXX_STANDARD=20 \
      -DCMAKE_CUDA_STANDARD=20 \
      -DCMAKE_INSTALL_PREFIX=/hypre/cuda \
      -DCUDA_PATH=/usr/local/cuda \
      -DHYPRE_ENABLE_CUDA=ON \
      -DHYPRE_BUILD_EXAMPLES=OFF \
      -DHYPRE_BUILD_TESTS=OFF \
      -DHYPRE_ENABLE_UMPIRE=OFF
cmake --build hypre/src/build_cuda
cmake --install hypre/src/build_cuda

cmake -S hypre/src \
      -B hypre/src/build_hip \
      -G Ninja \
      -DCMAKE_C_COMPILER=/usr/lib/ccache/gcc \
      -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
      -DCMAKE_HIP_ARCHITECTURES=gfx942 \
      -DGPU_TARGETS=gfx942 \
      -DBUILD_SHARED_LIBS=0 \
      -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
      -DCMAKE_CXX_STANDARD=20 \
      -DCMAKE_HIP_STANDARD=20 \
      -DCMAKE_INSTALL_PREFIX=/hypre/hip \
      -DHYPRE_ENABLE_HIP=ON \
      -DHYPRE_BUILD_EXAMPLES=OFF \
      -DHYPRE_BUILD_TESTS=OFF \
      -DHYPRE_ENABLE_UMPIRE=OFF
cmake --build hypre/src/build_hip
cmake --install hypre/src/build_hip
