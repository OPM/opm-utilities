#!/usr/bin/env bash

set +e
script_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
source $script_dir/set_environment.sh

#Set up options file for cmake
cat << EOF > "$opm_git_dir/options.cmake"
set(ERT_ROOT $ert_git_dir/install CACHE STRING "ERT root directory")
set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Build type (Release, Debug, etc)")
EOF

#Set which modules to compile
modules="\
opm-parser \
opm-core \
dune-cornerpoint \
opm-autodiff \
opm-polymer \
opm-material \
opm-porsol \
opm-upscaling \
opm-benchmarks"

#Function which clones or updates from a GIT repository
function clone_or_update() {
	local git_url="$1"
	local src_dir="$2"

	if [ -d $src_dir ]; then
		cd $src_dir
		git pull origin master
	else
		git clone --recursive $git_url $src_dir
	fi
}

#Function which downloads from git, creates a standardized
#build directory, and builds using cmake/make
function compile_module() {
	local src_dir="$1"
	local build_dir="$2"

	mkdir -p $build_dir
	cd $build_dir

	cmake -C ../options.cmake $src_dir
	make
}

# Runs tests
function run_tests() {
	local build_dir=$1
	cd $build_dir
	make test
}

#Fetch and compile all the OPM modules
for module in $modules; do
	git_url="https://github.com/OPM/$module"
	src_dir="$opm_git_dir/$module"
	build_dir="$opm_git_dir/$module-build"

	echo =======================$module-CLONE======================
	clone_or_update "$git_url" "$src_dir"
	echo =======================$module-COMPILE====================
	compile_module "$src_dir" "$build_dir"
	echo =======================$module-TEST=======================
	run_tests "$build_dir"
	echo =======================$module-END========================
done
