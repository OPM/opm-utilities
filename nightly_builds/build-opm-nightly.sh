#!/bin/bash

DIST=$1
WORKSPACE=$HOME

mkdir -p $HOME/debs/$DIST

# Wipe local package link
rm -f $HOME/debs/$DIST/local-apt

# We build in a temporary directory
TMPDIR=`mktemp -d`

pushd $TMPDIR
mkdir pdebuild-tmp
TODAY=`date --rfc-3339=date`
mkdir -p $WORKSPACE/debs/$DIST/nightly/$TODAY
ln -sf $WORKSPACE/debs/$DIST/nightly/$TODAY $HOME/debs/$DIST/local-apt

STATUS=0
for REPO in cwrap libecl opm-common opm-parser opm-output opm-material opm-grid opm-core ewoms opm-simulators opm-upscaling
do
  if [ "$REPO" == "libecl" ] || [ "$REPO" == "cwrap" ]
  then
    git clone --depth 1 https://github.com/Statoil/$REPO
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
  if [ "$REPO" == "cwrap" ]
  then
    sed -e 's/setuptools_scm/setuptools/g' -e s"/use_scm_version=.*/version = '$TODAY-git$REV',/g" -i setup.py
    echo "__version__ = '$TODAY-git$REV'" >> cwrap/__init__.py
  fi
  dch -b -v "$TODAY-git$REV-1~$DIST" -D $DIST --empty --force-distribution "New nightly build"
  DIST=$DIST pdebuild -- --buildresult $WORKSPACE/debs/$DIST/nightly/$TODAY --buildplace $TMPDIR/pdebuild-tmp --configfile $WORKSPACE/debs/$DIST/pbuilderrc
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
  tail -n6 $WORKSPACE/debs/$DIST/daily > $WORKSPACE/debs/$DIST/tmp
  mv $WORKSPACE/debs/$DIST/tmp $WORKSPACE/debs/$DIST/daily
  echo $TODAY >> $WORKSPACE/debs/$DIST/daily
  DAY=`date +"%u"`
  if test $DAY -eq 7
  then
    tail -n3 $WORKSPACE/debs/$DIST/monthly > $WORKSPACE/debs/$DIST/tmp
    mv $WORKSPACE/debs/$DIST/tmp $WORKSPACE/$DIST/debs/monthly
    echo $TODAY >> $WORKSPACE/debs/$DIST/monthly
  fi
  DATE=`date +"%d"`
  if test $DATE -eq 1
  then
    tail -n 4 $WORKSPACE/debs/$DIST/firstofmonth > $WORKSPACE/debs/$DIST/tmp
    mv $WORKSPACE/debs/$DIST/tmp $WORKSPACE/debs/$DIST/firstofmonth
    echo $TODAY >> $WORKSPACE/debs/$DIST/firstofmonth
  fi

  # Finally publish it
  $HOME/publish-apt-repo.sh $DIST
  test $? -eq 0 || STATUS=1
fi

# Clean up mess
rm -Rf $TMPDIR
exit $STATUS
