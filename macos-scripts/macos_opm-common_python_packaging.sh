#!/bin/bash

BUILD_JOBS=11
MACOS_VERSION=macosx-14.0-arm64 #change to macosx_26.0-arm64 when it works, now pip complains about unsupported platform tag
MACOS_TAG=macosx_14_0_arm64
OPM_VERSION=2026.4

brew install boost #cmake is already pre-installed on GitHub-hosted runners

if [ -d opm-common ]; then
    rm -rf opm-common
fi
git clone https://github.com/OPM/opm-common.git #--branch release/$OPM_VERSION

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

folder_path=$PWD

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
    make opmcommon_python -j${BUILD_JOBS}
    cd python
    python3 setup.py sdist bdist_wheel --plat-name $MACOS_VERSION --python-tag $tag
    #delocate-wheel -v dist/*$tag*.whl Uncoment this when macosx_26.0-arm64 works, now pip complains about unsupported platform tag
    cp dist/*$tag*.whl ../../wheelhouse
    popd
    deactivate
    rm -rf $tag 
    ${python_versions[$tag]} -m venv v$tag
    source v$tag/bin/activate
    pip install wheelhouse/opm-$OPM_VERSION-$tag-$MACOS_TAG.whl
    python -m unittest discover -s opm-common/python/tests
    if [[ $? -ne 0 ]]; then
      echo "Python unit tests failed for $tag. Exiting."
      exit 1
    fi
    deactivate
    rm -rf v$tag
done

echo "All good, the unit tests passed in all Python versions built wheels."
