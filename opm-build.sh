#! /bin/bash

usage() {
    echo "Manages the build, update and install process of OPM modules"
    echo ""
    echo "Usage: $0 COMMAND SOURCE_DIR BUILD_DIR"
    echo ""
    echo "COMMAND is one of"
    echo "  update    Fetch the latest version of the module from the"
    echo "            git repository"
    echo "  cmake     run cmake on all modules"
    echo "  build     Build all binaries of the modules"
    echo "  install   Run 'make install' on all modules"
    echo ""
    echo "Additional parameters for cmake can be specified via the "
    echo "'CMAKE_FLAGS' environment variable, additional parameters "
    echo "for the 'make' command can be set via the 'MAKE_FLAGS' variable."
}

OPM_INSTALLED_MODULES=""
declare -A OPM_MODULE_SOURCE_DIR
declare -A PROCESSED_MODULES

declare -A OPM_MODULE_DEPENDS
OPM_MODULE_DEPENDS[opm-cmake]=""
OPM_MODULE_DEPENDS[opm-parser]="opm-cmake"
OPM_MODULE_DEPENDS[opm-material]="opm-cmake opm-parser"
OPM_MODULE_DEPENDS[opm-core]="opm-cmake opm-material"
OPM_MODULE_DEPENDS[dune-cornerpoint]="opm-cmake opm-core"
OPM_MODULE_DEPENDS[opm-autodiff]="opm-cmake opm-core dune-cornerpoint"

OPM_ORDERED_MODULES=""

find_all_modules() {
    OPM_INSTALLED_MODULES=""

    for TMP in "$SRC_ROOT_DIR"/*; do
        if ! test -d "$TMP"; then
            # skip non-directories
            continue
        fi

        # transform the directory name to the module name
        case "$TMP" in
            *opm-*)
                TMP2="$(echo "$TMP" | sed "s/.*\(opm-[a-z]*\).*/\1/")"
                ;;

            *dune-cornerpoint*)
                TMP2="dune-cornerpoint"
                ;;

            *)
                # the directory contains stuff which we're not sure about
                continue
                ;;
        esac

        OPM_INSTALLED_MODULES="$OPM_INSTALLED_MODULES $TMP2"
        OPM_MODULE_SOURCE_DIR["$TMP2"]="$TMP"
    done
    echo "Found the following modules: $OPM_INSTALLED_MODULES"
}

# order a list of modules according to their dependency graph. (the
# graph is assumed to be acylic and directed.)
order_module_list() {
    local ALL_MODS="$@"
    local CUR_MODULE

    for CUR_MODULE in $ALL_MODS; do
        order_module_list ${OPM_MODULE_DEPENDS[$CUR_MODULE]}

        MODULE_SOURCE_DIR=${OPM_MODULE_SOURCE_DIR[$CUR_MODULE]}
        if ! test -d "$MODULE_SOURCE_DIR"; then
            echo "required module '$CUR_MODULE' seems to be missing abort."
            exit 1
        fi

        if test "${PROCESSED_MODULES["$CUR_MODULE"]}" != "1"; then
            PROCESSED_MODULES["$CUR_MODULE"]="1"

            OPM_ORDERED_MODULES="$OPM_ORDERED_MODULES $CUR_MODULE"
        fi
    done
}

do_update() {
    echo "do update"
    for CUR_MODULE in $@; do
        SOURCE_DIR="${OPM_MODULE_SOURCE_DIR[$CUR_MODULE]}"
        echo "$CUR_MODULE: $CUR_MODULE; SOURCE_DIR: $SOURCE_DIR"
        if ! test -d "$SOURCE_DIR/.git"; then
            echo "$SOURCE_DIR seems to be not managed by git. skipping."
            continue
        fi

        GIT_BRANCH=$(GIT_DIR="$SOURCE_DIR/.git" git branch | grep "^\*" | sed -e "s/^\*[ ]*//")

        if test "$GIT_BRANCH" != "master"; then
            echo "$SOURCE_DIR is not on the 'master' branch. skipping."
            continue
        fi

        echo "Updating working copy of module $CUR_MODULE"
        (cd $SOURCE_DIR; git pull --rebase)
    done
}

do_cmake() {
    echo "do cmake"

    local MODS="$@"
    local CUR_MODULE
    ROOT_DIRS=""
    for CUR_MODULE in $MODS; do
        MODULE_SOURCE_DIR="${OPM_MODULE_SOURCE_DIR[$CUR_MODULE]}"
        MODULE_BUILD_DIR="$BUILD_ROOT_DIR/$CUR_MODULE"

        MODULE_ROOT_DIRS="$ROOT_DIRS -D${CUR_MODULE}_ROOT=${MODULE_SOURCE_DIR}"
    done

    for CUR_MODULE in $MODS; do
        MODULE_SOURCE_DIR="${OPM_MODULE_SOURCE_DIR[$CUR_MODULE]}"
        MODULE_BUILD_DIR="$BUILD_ROOT_DIR/$CUR_MODULE"

        mkdir -p $MODULE_BUILD_DIR
        echo "running: cmake  ${CMAKE_FLAGS} ${MODULE_ROOT_DIRS}"

        (cd $MODULE_BUILD_DIR; cmake ${CMAKE_FLAGS} ${MODULE_ROOT_DIRS}) || exit 1
    done
}

do_build() {
    echo "do build"

    local MODS="$@"
    local CUR_MODULE
    for CUR_MODULE in $MODS; do
        MODULE_SOURCE_DIR="${OPM_MODULE_SOURCE_DIR[$CUR_MODULE]}"
        MODULE_BUILD_DIR="$BUILD_ROOT_DIR/$CUR_MODULE"

        (cd $MODULE_BUILD_DIR; make ${MAKE_FLAGS}) || exit 1
    done
}

do_all() {
    echo "do all"

    local MODS="$@"
    local CUR_MODULE

    do_update $MODS

    for CUR_MODULE in $MODS; do
        MODULE_SOURCE_DIR="${OPM_MODULE_SOURCE_DIR[$CUR_MODULE]}"
        MODULE_BUILD_DIR="$BUILD_ROOT_DIR/$CUR_MODULE"

        do_cmake $CUR_MODULE
        do_build $CUR_MODULE
    done
}

do_install() {
    echo "do install"

    local MODS="$@"
    local CUR_MODULE

    for CUR_MODULE in $MODS; do
        MODULE_SOURCE_DIR="${OPM_MODULE_SOURCE_DIR[$CUR_MODULE]}"
        MODULE_BUILD_DIR="$BUILD_ROOT_DIR/$CUR_MODULE"

        (cd $MODULE_BUILD_DIR; make install) || exit 1
    done
}


if test "$#" -lt 3; then
    usage
    exit 0
fi

COMMAND="$1"
SRC_ROOT_DIR="$2"
BUILD_ROOT_DIR="$3"

find_all_modules
order_module_list $OPM_INSTALLED_MODULES

echo "running '$COMMAND' on the following modules:$ORDERED_MODULES"

case "$COMMAND" in
update)
        do_update $OPM_ORDERED_MODULES
        ;;

cmake)
        do_cmake $OPM_ORDERED_MODULES
        ;;

build)
        do_build $OPM_ORDERED_MODULES
        ;;

install)
        do_install $OPM_ORDERED_MODULES
        ;;

all)
        do_all $OPM_ORDERED_MODULES
        ;;

*)
        echo "Unknown command '$COMMAND'"
        echo ""
        usage
        exit 1
        ;;
esac

echo "$COMMAND $SRC_ROOT_DIR $BUILD_ROOT_DIR"
