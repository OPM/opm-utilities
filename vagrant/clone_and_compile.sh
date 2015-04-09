#!/usr/bin/env bash

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

opm_base_dir="$HOME/workspace/opm"
mkdir -p $opm_base_dir
cd $opm_base_dir

function clone_or_update() {
	local git_dir=$1
	local src_dir=$2
	if [ -d $src_dir ]; then
		cd $src_dir
		git pull origin master
	else
		git clone --recursive $git_dir $src_dir
	fi
}

# Clone ERT, compile, and install
ert_install_dir="$opm_base_dir/ert"
clone_or_update "https://github.com/Ensembles/ert.git" "$opm_base_dir/ert-src"
cd "$opm_base_dir/ert-src"
git reset --hard 4ed6e5608922d62c8741824fc4a27ba7a5a4afd6 #Require this version of ERT
mkdir -p "$opm_base_dir/ert-build"
cd "$opm_base_dir/ert-build"
cmake -DCMAKE_INSTALL_PREFIX="$ert_install_dir" "$opm_base_dir/ert-src/devel"
make
make install

#Set up options file for cmake
cat << EOF > "$opm_base_dir/options.cmake"
set(ERT_ROOT $ert_install_dir CACHE STRING "ERT root directory")
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


#Function which downloads from git, creates a standardized
#build directory, and builds using cmake/make
function fetch_and_compile_module() {
	echo =======================$module-BEGIN=====================
	local module_name="$1"
	local git_dir="$2"
	local src_dir="$opm_base_dir/$module_name"
	local build_dir="$opm_base_dir/$module_name-build"

	clone_or_update $git_dir $src_dir

	mkdir -p $build_dir
	cd $build_dir
	cmake -C ../options.cmake $src_dir
	make 
	echo =======================$module-TEST=======================
	make test
	echo =======================$module-END========================
}


#Fetch and compile all the OPM modules
for module in $modules; do
	git_path="https://github.com/OPM/$module"
	fetch_and_compile_module $module $git_path;
done
