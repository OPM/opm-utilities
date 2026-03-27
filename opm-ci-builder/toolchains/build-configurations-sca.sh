#!/bin/bash

declare -a USED_BTYPES

USED_BTYPES=(
    clang_lto
    coverage_gcov
    debug_iterator
    lto
    shared
)

BTYPES=""
CMAKE_TOOLCHAIN_FILES=""
BUILD_CONFIGS=""
for BTYPE in ${USED_BTYPES[*]}
do
    BTYPES+=" ${BTYPE}"
    CMAKE_TOOLCHAIN_FILES+=" /toolchains/${BTYPE}.cmake"
    if [ "$BTYPE" = "coverage_gcov" ] || [ "$BTYPE" = "debug_iterator" ]
    then
      BUILD_CONFIGS+=" Debug"
    else
      BUILD_CONFIGS+=" Release"
    fi
done

export BUILDTHREADS=${BUILDTHREADS:-12}
export TESTTHREADS=${TESTTHREADS:-16}
export CTEST_TIMEOUT=10000
export BTYPES
export CMAKE_TOOLCHAIN_FILES
export BUILD_CONFIGS
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=2
export OPM_TESTS_ROOT_PREDEFINED=/opm-tests
export sha1="master"
