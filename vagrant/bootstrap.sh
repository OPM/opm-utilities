#!/usr/bin/env bash

script_dir=/host

$script_dir/scripts/install_packages.sh

if [ ! -d /home/vagrant/opm-build-scripts ]; then
	ln -s $script_dir/scripts /home/vagrant/opm-build-scripts
fi
