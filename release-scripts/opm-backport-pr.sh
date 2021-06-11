#!/bin/sh
#
# A small script to backport a full PR onto the release. Takes the PR number
# as the only argument and assumes that remote https://github.com/OPM/opm-module
# is called upstream. You need to adjust the RELEASE variable below
PR=$1 # the PR number
RELEASE=2019.10.bogus# Release
UPSTREAM=upstream #The remote name of the repo https://github.com/OPM/opm-module
git checkout release/$RELEASE
git pull
SHA="$(git log --oneline upstream/master | grep "Merge pull request #$PR"| head -n 1 | cut -d \  -f 1)"
FSHA="$(git show --pretty="format:%h" $SHA~)"
echo "backporting PR $PR from $FSHA to $SHA"
git rebase --onto release/$RELEASE $FSHA $SHA && git checkout -b backport-of-pr-$PR
