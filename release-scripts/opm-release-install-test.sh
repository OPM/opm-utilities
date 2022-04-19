#!/bin/sh
#
set -e
# A small script that builds and installs each module with the others
# already installed (and not still lying around next to it) in favirious
# flavors
RELEASE=2019.10
version=release/$RELEASE
BUILD_CONFIGS="opts-parallel.cmake opts-seq.cmake"


print_help(){
    echo "Usage: dune-release-test.sh --branch=<branch> --flavor=<flavor>"
    echo
    echo "branch is the branch to checkout (e.g. release/2019.10). Default is $RELEASE"
    echo "flavor should either be unset (all flavors) or one of:"
    echo "- parallel: MPI parallel build."
    echo "- seq: sequential build."
}

while test $# -gt 0; do
    # get args
    set +e
    # stolen from configure...
    # when no option is set, this returns an error code
    arg=`expr "x$1" : 'x[^=]*=\(.*\)'`
    set -e
    case "$1" in
      --branch=*)
          branch=$arg
	  echo "Using branch $branch"
        ;;
      --flavor=*)
        BUILD_CONFIGS=opts-$arg.cmake
        ;;
      --help)
        print_help
	exit 0
        ;;
      --*)
      echo "Unknown argument" >&2
      print_help
      exit 1;
    esac
    shift
done

OPM_MODULES="opm-common opm-grid opm-material opm-models opm-simulators opm-upscaling"
DIR=$HOME/opm-release-test/
mkdir -p $DIR
cd $DIR

if ! test -e opts-parallel.cmake; then
    cat> "opts-parallel.cmake" <<EOF
set(USE_MPI ON         CACHE STRING "Use mpi")
set(BUILD_TESTING ON CACHE BOOL "Build tests")
set(CMAKE_FIND_PACKAGE_NO_PACKAGE_REGISTRY 1 CACHE BOOL "" FORCE)
set(BUILD_ECL_SUMMARY ON CACHE BOOL "Build summary.x")
set(BUILD_APPLICATIONS ON CACHE BOOL "Build applications")
set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type to use")
set(CMAKE_INSTALL_PREFIX "$HOME/opt/opm/" CACHE PATH "installation directory")
EOF
fi
if ! test -e opts-seq.cmake; then
    cat> "opts-seq.cmake" <<EOF
set(USE_MPI OFF         CACHE STRING "Use mpi")
set(BUILD_TESTING ON CACHE BOOL "Build tests")
set(CMAKE_FIND_PACKAGE_NO_PACKAGE_REGISTRY 1 CACHE BOOL "" FORCE)
set(BUILD_ECL_SUMMARY ON CACHE BOOL "Build summary.x")
set(BUILD_APPLICATIONS ON CACHE BOOL "Build applications")
set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type to use")
set(CMAKE_INSTALL_PREFIX "$HOME/opt/opm-seq/" CACHE PATH "installation directory")
set(CMAKE_DISABLE_FIND_PACKAGE_MPI ON CACHE BOOL "Turn off MPI")
EOF
fi

# rest of the modules
for mod in $OPM_MODULES; do
    if ! test -d $mod; then
	git clone https://github.com/OPM/$mod
    fi
    cd $mod
    git checkout $branch
    git pull
    cd $DIR
   
    for flavor in $BUILD_CONFIGS; do
	echo "Building module $mod with config $flavor"
	rm -rf build-$flavor
	mkdir build-$flavor
	cd build-$flavor
	(cmake -C ../$flavor ../$mod && make -j16 install && (cd $DIR; rm -rf build-$flavor))|| exit 1
	cd $DIR
	echo "finished building module $mod with $flavor."
    done
    rm -rf $mod
done
