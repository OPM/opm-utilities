#!/bin/bash

OPTIND=1
while getopts "b:c:C:d:e:g:n:o:p:r:R:t:T:" OPT
do
    case "${OPT}" in
        b) PROJECT_BINARY_DIR=${OPTARG} ;;
        c) CLEAN_DIRS=${OPTARG} ;;
        C) CONFIGURATIONS=${OPTARG} ;;
        d) DOCKER_IMAGE=${OPTARG} ;;
        e) EXTRA_FILES=${OPTARG} ;;
        g) ghprbCommentBody=${OPTARG} ;;
        n) NUM_COMMITS=${OPTARG} ;;
        o) OPM_MODULE=${OPTARG} ;;
        p) PATCH_FILE=${OPTARG} ;;
        r) OPM_TESTS_ROOT=${OPTARG} ;;
        R) REPO_ROOT=${OPTARG} ;;
        t) TYPE=${OPTARG} ;;
        T) TOOLCHAIN="-v ${OPTARG}:/toolchains" ;;
    esac
done

ROOT_DIR=${PROJECT_BINARY_DIR}/${TYPE}_${OPM_MODULE}

if test -n "$TRIGGER"
then
    ghprbCommentBody+=" $TRIGGER"
fi

if grep -q "$OPM_MODULE" <<< $ghprbCommentBody
then
    if grep -q -v https://github.com <<< $REPO_ROOT
    then
        sha1=$(echo $ghprbCommentBody | sed -r "s/.*${OPM_MODULE}=([^ ]+)/\1/g")
    else
        sha1=pull/$(echo $ghprbCommentBody | sed -r 's/.*${OPM_MODULE}=([0-9]+).*/\1/g')/merge
    fi
fi

# Clone the OPM repository
sha1=${sha1:-master}
if [ "$OPM_MODULE" = "opm-tests" ]
then
    git clone -b ${sha1} ${REPO_ROOT}/opm-simulators ${ROOT_DIR}
    test $? -eq 0 || exit 1
else
    echo git clone -b ${sha1} ${REPO_ROOT}/${OPM_MODULE} ${ROOT_DIR}
    git clone -b ${sha1} ${REPO_ROOT}/${OPM_MODULE} ${ROOT_DIR}
    test $? -eq 0 || exit 1
fi

if grep -q -v https://github.com <<< $REPO_ROOT
then
    REPO_ROOT="-e OPM_REPO_ROOT=/repos -v ${REPO_ROOT}:/repos -e absolute_revisions=1"
else
    REPO_ROOT="-e OPM_REPO_ROOT=$REPO_ROOT"
fi

if test -n "$PATCH_FILE"
then
    # Clone opm-tests for patching
    git clone ${OPM_TESTS_ROOT} ${ROOT_DIR}/opm-tests-patched
    test $? -eq 0 || exit 1

    OPM_TESTS_ROOT=${ROOT_DIR}/opm-tests-patched

    # Apply patch to ensure failure
    pushd ${OPM_TESTS_ROOT}

    if test -n "${NUM_COMMITS}" && test "${NUM_COMMITS}" -ge 2
    then
      git checkout -b base_branch
      ghprbCommentBody+=" opm-tests=base_branch"
      REPO_ROOT+=" -e absolute_revisions=1 -e OPM_TESTS_UPSTREAM=/build/opm-tests-patched"
    fi

    git am ${PATCH_FILE}
    popd
fi

# Run the build
if [ "$TYPE" = "sca" ]
then
    docker run --shm-size=2048m \
               --rm \
               -u $(id -u) \
               -v ${ROOT_DIR}:/build \
               -v ${PROJECT_BINARY_DIR}/ccache:/ccache \
               -v ${OPM_TESTS_ROOT}:/opm-tests \
               ${TOOLCHAIN} \
               --entrypoint /build/jenkins/static_analysis.sh \
               ${REPO_ROOT} \
               ${DOCKER_IMAGE}
    res=$?
else
    docker run --shm-size=2048m \
               --rm  \
               -u $(id -u) \
               -e ghprbCommentBody="${ghprbCommentBody}" \
               -e sha1=${sha1}\
               -v ${ROOT_DIR}:/build \
               -v ${PROJECT_BINARY_DIR}/ccache:/ccache \
               -v ${OPM_TESTS_ROOT}:/opm-tests \
               ${REPO_ROOT} \
               ${TOOLCHAIN} \
               ${DOCKER_IMAGE}
    res=$?
fi

if test $res -eq 0
then
    # Check for expected files
    MSG=""
    for config in $CONFIGURATIONS
    do
        if ! test -f ${ROOT_DIR}/${config}/testoutput.xml
        then
            MSG+="Expected file ${config}/testoutput.xml NOT found\\n"
        fi
    done
    for file in $EXTRA_FILES
    do
        if ! test -f ${ROOT_DIR}/${file}
        then
            MSG+="Expected file ${file} NOT found\\n"
        fi
    done
    if [ "$TYPE" = "update_data" ]
    then
        # Check that opm-tests HEAD is a branch called 'update*'
        # and that it has NUM_COMMITS commit
        pushd ${ROOT_DIR}/deps/opm-tests
        branch_head=$(git branch --show-current)
        if grep -q "update.*" <<< "$branch_head"
        then
            branch_size=$(git rev-list origin/master..HEAD | wc -l)
            if test $branch_size -ne ${NUM_COMMITS}
            then
                MSG+="Expected ${NUM_COMMITS} commit(s) in 'update' branch, got '${branch_size}'\\n"
            fi
        else
          MSG+="Expected branch in opm-tests to match 'update.*', got '${branch_head}'\\n"
        fi

        # Check that at least one error report pdfs was generated
        num_pdfs=$(ls -1 ${ROOT_DIR}/default/build-opm-simulators/failure_report/*.pdf | wc -l)
        if test $num_pdfs -lt 1
        then
            MSG+="No error reports found\\n"
        fi
        popd
    fi
else
    MSG="Docker returned error code ${res}"
fi

if [ "${CLEAN_DIRS}" = "ON" ] || [ "${CLEAN_DIRS}" = "1" ]
then
    rm -Rf ${ROOT_DIR}
fi

if test -n "${MSG}"
then
    echo -e ${MSG}
    exit 1
fi
