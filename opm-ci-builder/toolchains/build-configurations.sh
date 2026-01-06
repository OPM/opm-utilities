#!/bin/bash

declare -a AVAILABLE_BTYPES

AVAILABLE_BTYPES=(
    clang
    clang_lto
    debug
    hipify
    lto
    rocm
    serial
    serial_debug
    serial_shared
    shared
)

if ! grep -q "nodefault" <<< $ghprbCommentBody
then
    BTYPES="default"
    CMAKE_TOOLCHAIN_FILES="$TOOLCHAIN_DIR/default.cmake"
fi

for BTYPE in ${AVAILABLE_BTYPES[*]}
do
    if grep -q " ${BTYPE}" <<< $ghprbCommentBody
    then
        BTYPES+=" $BTYPE"
        CMAKE_TOOLCHAIN_FILES+=" $TOOLCHAIN_DIR/$BTYPE.cmake"
    fi
done

export LD_LIBRARY_PATH=$WORKSPACE/shared/install/lib:$WORKSPACE/serial-shared/install/lib:$LD_LIBRARY_PATH

export BUILDTHREADS=16
export TESTTHREADS=16
export CTEST_TIMEOUT=400
export BTYPES
export CMAKE_TOOLCHAIN_FILES
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=2
export OPM_TESTS_ROOT_PREDEFINED=/opm-tests
