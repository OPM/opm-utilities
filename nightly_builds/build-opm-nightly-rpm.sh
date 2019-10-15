#!/bin/bash

DIST=$1
WORKSPACE=$HOME

# We build in a temporary directory
TMPDIR=`mktemp -d`

pushd $TMPDIR
mkdir -p SOURCES
mkdir -p SRPMS

TODAY=`date --rfc-3339=date | sed -e 's/-/_/g'`
rm -rf $HOME/rpms/$DIST/$TODAY
mkdir -p $HOME/rpms/$DIST/$TODAY
rm -f $HOME/rpms/$DIST/today
ln -sf $HOME/rpms/$DIST/$TODAY $HOME/rpms/$DIST/today

mock -r $DIST --clean
STATUS=0
REPOS="opm-common opm-material opm-grid opm-models opm-simulators opm-upscaling"
for REPO in $REPOS
do
  git clone --depth 1 https://github.com/OPM/$REPO

  if ! test $? -eq 0
  then
    STATUS=1
    break
  fi

  pushd $REPO
  REV=`git rev-parse --short HEAD`

  SPECNAME=$REPO
	 
  sed -i -e "s/Version:.*$/Version: ${TODAY}_git$REV/g" -e 's/-\%{tag}//g' -e 's/-release//g' redhat/*.spec
  git commit -am"bump to nightly version"
  git archive -o $TMPDIR/SOURCES/$SPECNAME-${TODAY}_git$REV.tar.gz --prefix $REPO-${TODAY}_git$REV/ master
  rpmbuild --define "_topdir $TMPDIR" -bs redhat/*.spec
  mock -r $DIST --resultdir=$HOME/rpms/$DIST/$TODAY $TMPDIR/SRPMS/$SPECNAME-${TODAY}_git$REV-0.src.rpm

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
  tail -n6 $WORKSPACE/rpms/$DIST/daily > $WORKSPACE/rpms/$DIST/tmp
  mv $WORKSPACE/rpms/$DIST/tmp $WORKSPACE/rpms/$DIST/daily
  echo $TODAY >> $WORKSPACE/rpms/$DIST/daily

  # Only dailies for redhat to save storage
#  DAY=`date +"%u"`
#  if test $DAY -eq 7
#  then
#    tail -n3 $WORKSPACE/rpms/$DIST/monthly > $WORKSPACE/rpms/$DIST/tmp
#    mv $WORKSPACE/rpms/$DIST/tmp $WORKSPACE/$DIST/rpms/monthly
#    echo $TODAY >> $WORKSPACE/rpms/$DIST/monthly
#  fi
#  DATE=`date +"%d"`
#  if test $DATE -eq 1
#  then
#    tail -n 4 $WORKSPACE/rpms/$DIST/firstofmonth > $WORKSPACE/rpms/$DIST/tmp
#    mv $WORKSPACE/rpms/$DIST/tmp $WORKSPACE/rpms/$DIST/firstofmonth
#    echo $TODAY >> $WORKSPACE/rpms/$DIST/firstofmonth
#  fi

  # Finally publish it
  $HOME/publish-rpm-repo.sh $DIST
  test $? -eq 0 || STATUS=1
fi

# Clean up mess
rm -Rf $TMPDIR
exit $STATUS
