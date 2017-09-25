#!/bin/bash

# This creates and signs a apt repo of the debs to be included, then publishes
# it on opm-project.org.
# It uses the 'aptly' helper to build the repository (apt-get install aptly)
# You have to setup a GPG key on the user that runs it, and export the
# public key as repokey.gpg in the user's home directory

WORKSPACE=$HOME
DIST=xenial
REPO_URL=deb-builder@opm-project.org:/usr/share/nginx/package/nightly-xenial/

DIRS=`cat $WORKSPACE/daily $WORKSPACE/monthly $WORKSPACE/firstofmonth | sort -u`

# Create repo
aptly repo create -distribution=$DIST -architectures=amd64 -component=main opm-nightly
test $? -eq 0 || exit 1

# Import debs
for DIR in $DIRS
do
  aptly repo add opm-nightly $HOME/debs/$DIST/nightly/$DIR/*.deb
  test $? -eq 0 || exit 1
done

# Publish to local filesystem
aptly publish repo opm-nightly
test $? -eq 0 || exit 1
cp $HOME/repokey.gpg $HOME/.aptly/public

# Finally copy to webserver
rsync -r --delete $HOME/.aptly/public/* $REPO_URL
test $? -eq 0 || exit 1

# Remove published repo
aptly publish drop xenial
test $? -eq 0 || exit 1
aptly repo drop opm-nightly
test $? -eq 0 || exit 1
