#!/usr/bin/env bash

set +e
script_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
source $script_dir/set_environment.sh

#Function which clones or updates from a GIT repository
function clone_or_update() {
	local git_url=$1
	local src_dir=$2
	if [ -d $src_dir ]; then
		cd $src_dir
		git pull origin master
	else
		git clone --recursive $git_url $src_dir
	fi
}

# Clone ERT, compile, and install
clone_or_update "https://github.com/Ensembles/ert.git" "$ert_git_dir/src"
mkdir -p "$ert_git_dir/build"
cd "$ert_git_dir/build"
cmake -DCMAKE_INSTALL_PREFIX="$ert_git_dir/install" "$ert_git_dir/src/devel"
make
make install
