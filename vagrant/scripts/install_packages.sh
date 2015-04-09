#!/usr/bin/env bash

#This script installs prerequisites for compiling OPM packages

#Make sure that script exits on failure, and that all commands are printed
set -e
set -x

install_check_file="$HOME/.opm_deps_installed"
if [ -f $install_check_file ]; then
	echo $install_check_file "exists, skipping install procedure"
	echo "install_packages.sh run " `date` ", but did nothing" >> $install_check_file
else
	#Make sure we have updated URLs to packages etc.
	sudo apt-get update -y

	#Packages needed for add-apt-repository
	sudo apt-get install -y python-software-properties software-properties-common

	#Add PPAs we need
	sudo add-apt-repository -y ppa:opm/ppa #OPM packages
	sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test #Updated GCC packages

	#Update package list
	sudo apt-get update -y

	#Misc libraries
	sudo apt-get install -y \
	liblas-dev \
	liblas-c-dev \
	libboost1.55-all-dev \
	libsuperlu3-dev \
	libsuitesparse-dev \
	libumfpack5.6.2 \
	libdune-common-dev \
	libdune-geometry-dev \
	libdune-grid-dev \
	libdune-istl-dev \
	libeigen3-dev \
	qt4-default

	#Build tools
	sudo apt-get install -y \
	g++-4.9 \
	build-essential \
	gfortran \
	pkg-config \
	cmake \
	cmake-curses-gui \
	cmake-qt-gui 

	sudo apt-get install -y \
	doxygen \
	ghostscript \
	texlive-latex-recommended \
	pgf 

	sudo apt-get install -y \
	git-core

	sudo apt-get install -y \
	libumfpack5.6.2 \
	libsuitesparse-dev \
	libert.ecl-dev 

	echo "install_packages.sh run " `date` >> $install_check_file
fi

