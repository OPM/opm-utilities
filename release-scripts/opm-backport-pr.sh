#!/bin/sh
#
# A small script to back-port a full PR onto a release branch.  Takes
# the PR number as a mandatory command line argument and, optionally,
# two more arguments--one for the release ID (e.g., 2025.04) and one
# for the name of the upstream repository
# https://github.com/OPM/opm-module (default "upstream").
#
# The script assumes that it's being run in a local workspace of an
# OPM module.
#
# Before running this script, please run 'git remote update' to ensure
# the commits you want are in your local repository of the module for
# which you're back-porting PRs.  Then, run the script from this local
# repository.
#
# Example: Back-port PR 1729 of module opm-grid to release
# branch release/2024.10 from 'upstream' remote repository (default).
#
#    cd path/to/opm-grid
#    git remote update --prune
#
#    sh path/to/opm-utilities/release-scripts/opm-backport-pr.sh 1729 2024.10

if [ $# -lt 1 ]; then
    echo "Must supply at least the PR number (e.g., '8192') as an argument"
    exit 2 # Status code '2' is bash(1) convention for incorrect usage.
fi

set -e
set -x

# PR number.
PR=$1

# Release ID.
RELEASE=${2:-2025.04}

# Local name of the main upstream repo, https://github.com/OPM/<opm-module>
UPSTREAM=${3:-upstream}

# Source branch from which to merge PRs.
src_branch=master

git switch release/$RELEASE
git pull --ff-only $UPSTREAM release/$RELEASE

SHA=$(git log --oneline ${UPSTREAM}/${src_branch} | \
          awk -v search="Merge pull request #${PR}[[:space:]]+" \
              '$0~search{print $1; exit}')
FSHA="$(git show --pretty="format:%h" $SHA~)"

echo "backporting PR $PR from $FSHA to $SHA"
git rebase --onto release/$RELEASE $FSHA $SHA && \
    git switch --create=backport-of-pr-$PR
