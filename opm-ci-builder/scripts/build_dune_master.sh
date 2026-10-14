#!/bin/bash

set -e

declare -A dune_repo
dune_repo[dune-alugrid]=https://gitlab.dune-project.org/extensions/dune-alugrid.git
dune_repo[dune-common]=https://gitlab.dune-project.org/core/dune-common.git
dune_repo[dune-fem]=https://gitlab.dune-project.org/dune-fem/dune-fem.git
dune_repo[dune-geometry]=https://gitlab.dune-project.org/core/dune-geometry.git
dune_repo[dune-grid]=https://gitlab.dune-project.org/core/dune-grid.git
dune_repo[dune-istl]=https://gitlab.dune-project.org/core/dune-istl.git
dune_repo[dune-localfunctions]=https://gitlab.dune-project.org/core/dune-localfunctions.git
dune_repo[dune-uggrid]=https://gitlab.dune-project.org/staging/dune-uggrid.git

declare -A dune_version
dune_version[dune-alugrid]=master
dune_version[dune-common]=master
dune_version[dune-fem]=master
dune_version[dune-geometry]=master
dune_version[dune-grid]=master
dune_version[dune-istl]=master
dune_version[dune-localfunctions]=master
dune_version[dune-uggrid]=master

DESTDIR=/dune/master
BUILDDIR=$(mktemp -d -t build.dune.XXXXX)

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
  git clone ${dune_repo[$repo]} $BUILDDIR/$repo
  git -C $BUILDDIR/$repo checkout ${dune_version[$repo]}
  cmake    -S $BUILDDIR/$repo \
           -B $BUILDDIR/$repo/build \
           -GNinja \
           -DCMAKE_BUILD_TYPE=Release \
           -DCMAKE_DISABLE_FIND_PACKAGE_Doxygen=ON \
           -DCMAKE_C_COMPILER=/usr/lib/ccache/gcc \
           -DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++ \
           -DBUILD_SHARED_LIBS=OFF \
           -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
           -DDUNE_ENABLE_PYTHONBINDINGS=OFF \
           -DCMAKE_INSTALL_PREFIX=$DESTDIR \
           -DCMAKE_PREFIX_PATH=$DESTDIR
  cmake --build $BUILDDIR/$repo/build
  cmake --install $BUILDDIR/$repo/build
done
