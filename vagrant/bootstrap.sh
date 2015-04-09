#!/usr/bin/env bash

script_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

$script_dir/scripts/install_packages.sh

if [ ! -f $HOME/build_from_git.sh ]; then
	ln -s $script_dir/scripts/build_from_git.sh $HOME/build_from_git.sh
fi
