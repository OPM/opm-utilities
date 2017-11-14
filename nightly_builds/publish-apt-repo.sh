#!/bin/bash

# This creates and signs a apt repo of the debs to be included, then publishes
# it on opm-project.org

WORKSPACE=$HOME
DIST=$1

DIRS=`cat $WORKSPACE/debs/$DIST/daily $WORKSPACE/debs/$DIST/monthly $WORKSPACE/debs/$DIST/firstofmonth | sort -u`

# Create repo
aptly repo create -distribution=$DIST -architectures=amd64 -component=main opm-nightly-$DIST
test $? -eq 0 || exit 1

# Import debs
for DIR in $DIRS
do
  aptly repo add opm-nightly-$DIST $HOME/debs/$DIST/nightly/$DIR/*.deb
  test $? -eq 0 || exit 1
done

# Publish to local filesystem
aptly publish repo opm-nightly-$DIST
test $? -eq 0 || exit 1
cp $HOME/repokey.gpg $HOME/.aptly/public

# Finally copy to webserver
rsync -r --delete $HOME/.aptly/public/* deb-builder@opm-project.org:/usr/share/nginx/package/nightly-$DIST/
test $? -eq 0 || exit 1

# Remove published repo
aptly publish drop $DIST
test $? -eq 0 || exit 1
aptly repo drop opm-nightly-$DIST
test $? -eq 0 || exit 1
