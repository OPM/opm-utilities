#!/usr/bin/env bash

# This script installs all OPM packages

#Make sure that script exits on failure, and that all commands are printed
set -e
set -x

# Make sure we have updated URLs to packages etc.
sudo apt-get update -y

# Packages needed for add-apt-repository
sudo apt-get install -y python3-software-properties software-properties-common

# Add PPA for the OPM packages
sudo add-apt-repository -y ppa:opm/ppa

# Update package list again
sudo apt-get update -y

# OPM packages
sudo apt-get install -y mpi-default-bin
sudo apt-get install -y libopm-simulators-bin

# Other utilities that are required by tutorials etc.
sudo apt-get install unzip -y
