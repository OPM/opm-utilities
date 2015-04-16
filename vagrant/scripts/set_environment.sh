#!/usr/bin/env bash

#Script that sets up the environment for us

#Make sure that script exits on failure, and that all commands are printed
set -e
set -x

#I experienced some issues building OPM related to undefined LC_ALL
#Therefore set these explicitly here
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
locale-gen en_US.UTF-8
sudo dpkg-reconfigure locales

#Set GCC version, and set colors to use
export GCC_COLORS=1
export CC=/usr/bin/gcc-4.9
export CXX=/usr/bin/g++-4.9

#Set the default opm directories to use
opm_git_dir="$HOME/workspace/opm-git"
mkdir -p $opm_git_dir

ert_git_dir="$HOME/workspace/ert-git"
mkdir -p $ert_git_dir

opm_tgz_dir="$HOME/workspace/opm-tgz"
mkdir -p $opm_tgz_dir

#Set number of parallel jobs to use with make
export MAKEFLAGS="-j 3"
