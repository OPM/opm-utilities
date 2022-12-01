# This dockerfile builds the docker image / container
# for OPM, which then is easy to publish on docker hub
# or similar.

# Useful commands use:
# $ docker build -t opm_docker_image .
# $ docker build --build-arg opm_version=testing-t opm_docker_image .
# $ docker build --build-arg opm_version=nightly -t opm_docker_image .
# $ docker build --build-arg opm_version=2017-09-25 -t opm_docker_image .
# $ docker tag opm_docker_image openporousmedia/opmreleases:<version_number>
# $ docker login
# $ docker push
# $ docker run -v <HOST_DIR>:/shared_host opm_docker_image flow output_dir="/shared_host/output" "/shared_host/<DECK>"

# Use most recent version of ubuntu
FROM ubuntu:22.04

ARG opm_version=release

# Make sure we have updated URLs to packages etc.
RUN apt-get update -y

# Packages needed for add-apt-repository
RUN apt-get install -y software-properties-common wget apt-transport-https openssh-client

# Add apt-repo for the OPM packages
# For the release repository, we should use "ppa:opm/ppa"
# For the testing repository, we should use "ppa:opm/testing"
# For the nightly repository, we should use http://opm-project.org/package/xenial-bionic
RUN if [ "$opm_version" = "release" ]; then apt-add-repository ppa:opm/ppa; fi
RUN if [ "$opm_version" = "testing" ]; then apt-add-repository ppa:opm/testing; fi

RUN if test "$opm_version" != "release" && test "$opm_version" != "testing"; then  wget -qO - https://opm-project.org/package/nightly-bionic/repokey.gpg | apt-key add -; fi

RUN if test "$opm_version" != "release" && test "$opm_version" != "testing"; then apt-add-repository https://opm-project.org/package/nightly-bionic; fi

# Update package list again
RUN apt-get update -y

# OPM packages
RUN if test "$opm_version" = "release" || test "$opm_version" = "testing" || test "$opm_version" = "nightly"; then apt-get install -y libopm-simulators-bin; else apt-get install -y libopm-simulators-bin=$opm_version* \
                                       libopm-simulators=$opm_version* \
                                       libopm-grid=$opm_version* \
                                       libopm-common=$opm_version*; fi
RUN apt-get install openmpi-bin -y

# Other utilities that are required by tutorials etc.
RUN apt-get install unzip -y

# Create shared directory
RUN mkdir /shared_host
VOLUME /shared_host

RUN adduser opm
USER opm
