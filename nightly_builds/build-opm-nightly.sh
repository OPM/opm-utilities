#!/bin/bash

# This scripts builds nightly debs for OPM on a specified distro
# and then publishes them in an apt-repo

DIST=xenial
WORKSPACE=$HOME

mkdir -p $HOME/debs/$DIST

# Wipe local package link
rm -f $HOME/debs/$DIST/local-apt

# We build in a temporary directory
TMPDIR=`mktemp -d`

pushd $TMPDIR
mkdir pdebuild-tmp
TODAY=`date --rfc-3339=date`
mkdir -p $HOME/debs/$DIST/nightly/$TODAY
ln -sf $HOME/debs/$DIST/nightly/$TODAY $HOME/debs/$DIST/local-apt

STATUS=0
for REPO in libecl opm-common opm-parser opm-output opm-material opm-grid opm-core ewoms opm-simulators opm-upscaling
do
  if [ "$REPO" == "libecl" ]
  then
    git clone --depth 1 https://github.com/Statoil/libecl
  else
    git clone --depth 1 https://github.com/OPM/$REPO
  fi
  if ! test $? -eq 0
  then
    STATUS=1
    break
  fi
  pushd $REPO
  REV=`git rev-parse --short HEAD`
  dch -b -v "$TODAY-git$REV-1~$DIST" -D $DIST --empty --force-distribution "New nightly build"
  DIST=$DIST pdebuild -- --buildresult $HOME/debs/$DIST/nightly/$TODAY --buildplace $TMPDIR/pdebuild-tmp
  if ! test $? -eq 0
  then
    STATUS=1
    break
  fi
  popd
done
popd

if test $STATUS -eq 0
then
  tail -n6 $WORKSPACE/daily > $WORKSPACE/tmp
  mv $WORKSPACE/tmp $WORKSPACE/daily
  echo $TODAY >> $WORKSPACE/daily
  DAY=`date +"%u"`
  if test $DAY -eq 7
  then
    tail -n3 $WORKSPACE/monthly > $WORKSPACE/tmp
    mv $WORKSPACE/tmp $WORKSPACE/monthly
    echo $TODAY >> $WORKSPACE/monthly
  fi
  DATE=`date +"%d"`
  if test $DATE -eq 1
  then
    tail -n 4 $WORKSPACE/firstofmonth > $WORKSPACE/tmp
    mv $WORKSPACE/tmp $WORKSPACE/firstofmonth
    echo $TODAY >> $WORKSPACE/firstofmonth
  fi

  # Finally publish it
  $HOME/publish-apt-repo.sh
  test $? -eq 0 || STATUS=1
fi

# Clean up mess
rm -Rf $TMPDIR
exit $STATUS
