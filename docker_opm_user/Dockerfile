# This dockerfile builds the docker image / container
# for OPM, which then is easy to publish on docker hub
# or similar.

# Useful commands use: 
# $ docker build -t opm_docker_image .
# $ docker tag opm_docker_image openporousmedia/opmreleases:<version_number>
# $ docker login
# $ docker push
# $ docker run -v <HOST_DIR>:/shared_host opm_docker_image flow output_dir="/shared_host/output" "/shared_host/<DECK>"

# Use most recent version of ubuntu
FROM ubuntu:latest

# Make sure we have updated URLs to packages etc.
RUN apt-get update -y

# Packages needed for add-apt-repository
RUN apt-get install -y python-software-properties software-properties-common

# Add PPA for the OPM packages 
##########################################################
##########  (NOTE: testing repository here!) #############
##########################################################
# For the release repository, we should use "ppa:opm/ppa"
RUN add-apt-repository -y ppa:opm/ppa

# Update package list again
RUN apt-get update -y

# OPM packages
RUN apt-get install libopm-core1 -y
RUN apt-get install libopm-simulators1-bin -y
RUN apt-get install libopm-upscaling1-bin -y
RUN apt-get install openmpi-bin -y

# Other utilities that are required by tutorials etc.
RUN apt-get install unzip -y

# Create shared directory
RUN mkdir /shared_host
VOLUME /shared_host
