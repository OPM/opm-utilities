#!/usr/bin/env bash

set +e

script_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

$script_dir/build_ert_from_git.sh
$script_dir/build_opm_from_git.sh
$script_dir/build_ResInsight_from_git.sh

