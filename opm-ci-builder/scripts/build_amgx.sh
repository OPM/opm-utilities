#!/bin/bash

set -e

git clone --recursive -b $1 https://github.com/nvidia/amgx
mkdir -p amgx/build
cd amgx/build
cmake .. -GNinja -DCMAKE_C_COMPILER=/usr/lib/ccache/gcc \
                 -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
                 -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc \
                 -DCMAKE_CUDA_COMPILER_LAUNCHER=/usr/bin/ccache \
                 -DCMAKE_CUDA_ARCHITECTURES=80 -DCUDA_ARCH=80 \
                 -DCMAKE_INSTALL_PREFIX=/usr/local
ninja install
