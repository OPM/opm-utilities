#!/bin/bash

set -e

cat >> /etc/openmpi/openmpi-mca-params.conf <<EOCONF

rmaps_base_oversubscribe = 1
hwloc_base_use_hwthreads_as_cpus = 1
hwloc_base_binding_policy = none

EOCONF

usermod -u $1 ubuntu
groupmod -g $1 ubuntu

su ubuntu -c "git config --global user.name jenkins4opm"
su ubuntu -c "git config --global user.email jenkins4opm@ci.opm-project.org"

update-alternatives --install /usr/bin/gfortran gfortran-14 /usr/bin/gfortran-14 100
update-alternatives --install /usr/bin/gcc gcc-14 /usr/bin/gcc-14 100
update-alternatives --install /usr/bin/g++ g++-14 /usr/bin/g++-14 100
update-alternatives --install /usr/bin/clang++ clang++-20 /usr/bin/clang++-20 100
update-alternatives --install /usr/bin/clang clang-20 /usr/bin/clang-20 100
update-alternatives --install /usr/bin/clang-tidy clang-tidy-20 /usr/bin/clang-tidy-20 100
update-alternatives --install /usr/bin/run-clang-tidy run-clang-tidy-20 /usr/bin/run-clang-tidy-20 100
update-alternatives --install /usr/bin/gcov gcov-14 /usr/bin/gcov-14 100

ln -sf /usr/bin/ccache /usr/lib/ccache/clang
ln -sf /usr/bin/ccache /usr/lib/ccache/clang++
