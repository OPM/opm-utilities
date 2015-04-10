#!/usr/bin/env bash

script_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

$script_dir/scripts/install_packages.sh

if [ ! -d $HOME/opm-build-scripts ]; then
	ln -s $script_dir/scripts $HOME/opm-build-scripts
fi
