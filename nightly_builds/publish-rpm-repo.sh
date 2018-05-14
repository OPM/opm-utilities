#!/bin/bash

# This creates and signs a apt repo of the debs to be included, then publishes
# it on opm-project.org

WORKSPACE=$HOME
DIST=$1

if grep -q 7 <<< $DIST
then
  RELEASEVER=7
else
  RELEASEVER=6
fi

DIRS=`cat $WORKSPACE/rpms/$DIST/daily $WORKSPACE/rpms/$DIST/monthly $WORKSPACE/rpms/$DIST/firstofmonth | sort -u`

# Create repo
TMPDIR=`mktemp -d`
pushd $TMPDIR

# Import rpms
for DIR in $DIRS
do
  cp $HOME/rpms/$DIST/$DIR/*.rpm .
  test $? -eq 0 || exit 1
done
for RPM in *rpm
do
  rpm --addsign $RPM
done
cp $HOME/rpms/$DIST/static/*.rpm .

# Create repo
createrepo .

# Finally copy to webserver
rsync -r --delete $TMPDIR/* deb-builder@opm-project.org:/usr/share/nginx/package/nightly-redhat/$RELEASEVER
test $? -eq 0 || exit 1

popd
rm -Rf $TMPDIR
