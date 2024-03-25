#!/bin/sh
#
# A small script to backport a full PR onto the release. Takes the PR number
# as the only argument and assumes that remote https://github.com/OPM/opm-module
# is called upstream. You need to adjust the RELEASE variable below
#
# Before running, do 'git remote update' to ensure the commits you want are in your repo.
# Run the script from the local repository of the module you are backporting in.
set -e
set -x
PR=4249 # the PR number
RELEASE=2022.10
UPSTREAM=upstream #The remote name of the repo https://github.com/OPM/<opm-module>
git checkout release/$RELEASE
git pull $UPSTREAM release/$RELEASE
SHA="$(git log --oneline upstream/master | grep "Merge pull request #$PR"| head -n 1 | cut -d \  -f 1)"
FSHA="$(git show --pretty="format:%h" $SHA~)"
echo "backporting PR $PR from $FSHA to $SHA"
git rebase --onto release/$RELEASE $FSHA $SHA && git checkout -b backport-of-pr-$PR



# https://github.com/OPM/opm-common/pull/3186
# https://github.com/OPM/opm-common/pull/3192
# https://github.com/OPM/opm-common/pull/3193
# https://github.com/OPM/opm-common/pull/3195
# https://github.com/OPM/opm-common/pull/3198
# https://github.com/OPM/opm-common/pull/3203
# https://github.com/OPM/opm-common/pull/3205

# https://github.com/OPM/opm-models/pull/741
# https://github.com/OPM/opm-models/pull/746
# https://github.com/OPM/opm-models/pull/748

# https://github.com/OPM/opm-simulators/pull/4185
# https://github.com/OPM/opm-simulators/pull/4187
# https://github.com/OPM/opm-simulators/pull/4194
# https://github.com/OPM/opm-simulators/pull/4200
# https://github.com/OPM/opm-simulators/pull/4207
# https://github.com/OPM/opm-simulators/pull/4217
# https://github.com/OPM/opm-simulators/pull/4223

# https://github.com/OPM/opm-upscaling/pull/367


# https://github.com/OPM/opm-simulators/pull/4212
# https://github.com/OPM/opm-simulators/pull/4242
# https://github.com/OPM/opm-simulators/pull/4243
# https://github.com/OPM/opm-simulators/pull/4249
