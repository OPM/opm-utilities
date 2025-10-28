#!/bin/sh
#
# A small script to generate macOS pip wheels of opm-common Python,
# saved in the weelhouse folder created at the execution's location. 
# Takes as arguments the opm-common branch (default "master"),
# the no. version of macOS (default "14.0"), architecture (default 
# "arm64", and number of cores to build opmcommon_python (default "5").
#
# Example: Generate the macOS wheels for the 2026.04 release
# for macOS 14 (Sonoma) arm64 using five cores.
#
#    sh path/to/opm-utilities/macos-scripts/macos_opm-common_python_packaging.sh release/2026.04 14.0 arm64 5
#

set -e

BRANCH=${1:-master}
VERSION=${2:-14.0} #change to 26.0 when it works, now pip complains about unsupported platform tag
ARCHITECTURE=${3:-arm64}
JOBS=${4:-11}

brew install boost #cmake is already pre-installed on GitHub-hosted runners

if [ -d opm-common ]; then
    rm -rf opm-common
fi
git clone https://github.com/OPM/opm-common.git --branch $BRANCH

opm_version=$(grep "Version" opm-common/dune.module)

declare -A python_versions
python_versions[cp39-cp39]=/opt/homebrew/bin/python3.9
python_versions[cp310-cp310]=/opt/homebrew/bin/python3.10
python_versions[cp311-cp311]=/opt/homebrew/bin/python3.11
python_versions[cp312-cp312]=/opt/homebrew/bin/python3.12
python_versions[cp313-cp313]=/opt/homebrew/bin/python3.13
python_versions[cp314-cp314]=/opt/homebrew/bin/python3.14

if [ -d wheelhouse ]; then
    rm -rf wheelhouse
fi
mkdir -p wheelhouse

for tag in cp314-cp314 cp313-cp313 cp312-cp312 cp311-cp311 cp310-cp310 cp39-cp39
do  if [ -d $tag ]; then
     rm -rf $tag
    fi
    mkdir $tag && pushd $tag
    ${python_versions[$tag]} -m venv v$tag
    source v$tag/bin/activate
    python3 -m pip install pip --upgrade
    python3 -m pip install wheel setuptools twine pytest-runner delocate scikit-build cmake
    cmake -DPYTHON_EXECUTABLE=$(which python) -DOPM_ENABLE_DUNE=0 -DUSE_MPI=0 -DWITH_NATIVE=0 -DBoost_USE_STATIC_LIBS=1 -DOPM_ENABLE_PYTHON=ON ../opm-common
    make opmcommon_python -j${JOBS}
    cd python
    python3 setup.py sdist bdist_wheel --plat-name macosx-$VERSION-$ARCHITECTURE --python-tag $tag
    #delocate-wheel -v dist/*$tag*.whl Uncoment this when macosx_26.0-arm64 works, now pip complains about unsupported platform tag
    cp dist/*$tag*.whl ../../wheelhouse
    popd
    deactivate
    rm -rf $tag 
    ${python_versions[$tag]} -m venv v$tag
    source v$tag/bin/activate
    if [[ "${opm_version:14:1}" == "0" ]]; then
      pip install wheelhouse/opm-${opm_version:9:5}${opm_version:15:1}-$tag-macosx_${VERSION:0:2}_${VERSION: -1}_$ARCHITECTURE.whl
    else
      pip install wheelhouse/opm-${opm_version:9:7}-$tag-macosx_${VERSION:0:2}_${VERSION: -1}_$ARCHITECTURE.whl
    fi
    python -m unittest discover -s opm-common/python/tests
    deactivate
    rm -rf v$tag
done

rm -rf opm-common
