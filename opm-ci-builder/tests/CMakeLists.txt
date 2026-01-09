cmake_minimum_required(VERSION 3.23)

project(opm_ci_tests)

set(REPO_ROOT "https://github.com/OPM"
    CACHE STRING "Git repository root URL/directory")
set(OPM_TESTS_ROOT "https://github.com/OPM/opm-tests"
    CACHE STRING "Git repository root URL/directory")
set(DOCKER_IMAGE ""
    CACHE STRING "docker image to run tests for")
set(TOOLCHAIN_DIR "" CACHE STRING "Externally provided toolchains")

option(CLEAN_DIRS "Clean directories after test finishes?" ON)

if(NOT DOCKER_IMAGE)
  message(FATAL_ERROR "DOCKER_IMAGE must be set")
endif()

file(MAKE_DIRECTORY ${PROJECT_BINARY_DIR}/ccache)

enable_testing()

if(TOOLCHAIN_DIR)
  set(TOOLCHAIN -T ${TOOLCHAIN_DIR})
endif()

if(OPM_TESTS_ROOT MATCHES "https://github.com")
  execute_process(COMMAND test -d ${PROJECT_BINARY_DIR}/opm-tests || git clone ${OPM_TESTS_ROOT} ${PROJECT_BINARY_DIR}/opm-tests)
  set(OPM_TESTS_LOCAL_ROOT ${PROJECT_BINARY_DIR}/opm-tests)
else()
  set(OPM_TESTS_LOCAL_ROOT ${OPM_TESTS_ROOT})
endif()

foreach(module opm-common opm-grid opm-simulators opm-upscaling)
  add_test(
    NAME
      static_analysis+${module}
    COMMAND
      ${PROJECT_SOURCE_DIR}/build.sh
      -b ${PROJECT_BINARY_DIR}
      -c ${CLEAN_DIRS}
      -C "clang_lto coverage_gcov debug_iterator lto shared"
      -d ${DOCKER_IMAGE}
      -e "cppcheck-result.xml \
          clang-tidy-report.log \
          infer-out/report.xml \
          coverage.xml \
          debug_iterator/build-${module}/doc/doxygen/Warnings.log"
      -o ${module}
      -r ${OPM_TESTS_LOCAL_ROOT}
      -R ${REPO_ROOT}
      -t sca
      ${TOOLCHAIN}
  )

  add_test(
    NAME
      pull+${module}
    COMMAND
      ${PROJECT_SOURCE_DIR}/build.sh
      -b ${PROJECT_BINARY_DIR}
      -c ${CLEAN_DIRS}
      -C default
      -d ${DOCKER_IMAGE}
      -g "jenkins build this with downstreams please"
      -o ${module}
      -r ${OPM_TESTS_LOCAL_ROOT}
      -R ${REPO_ROOT}
      -t pull
      ${TOOLCHAIN}
  )
endforeach()

add_test(
  NAME
    pull+opm-tests
  COMMAND
    ${PROJECT_SOURCE_DIR}/build.sh
    -b ${PROJECT_BINARY_DIR}
    -c ${CLEAN_DIRS}
    -C default
    -d ${DOCKER_IMAGE}
    -g "jenkins build this with downstreams please"
    -o opm-tests
    -r ${OPM_TESTS_LOCAL_ROOT}
    -R ${REPO_ROOT}
    -t pull
    ${TOOLCHAIN}
)

foreach(module opm-common opm-grid opm-simulators)
  add_test(
    NAME
      update_data+${module}
    COMMAND
      ${PROJECT_SOURCE_DIR}/build.sh
      -b ${PROJECT_BINARY_DIR}
      -c ${CLEAN_DIRS}
      -C default
      -d ${DOCKER_IMAGE}
      -e data_diff
      -g "jenkins build this with downstreams failure_report update_data please"
      -n 1
      -o ${module}
      -p ${PROJECT_SOURCE_DIR}/spe1_force_failures.patch
      -r ${OPM_TESTS_LOCAL_ROOT}
      -R ${REPO_ROOT}
      -t update_data
      ${TOOLCHAIN}
  )

  add_test(
    NAME
      run+${module}
    COMMAND
      ${PROJECT_SOURCE_DIR}/build.sh
      -b ${PROJECT_BINARY_DIR}
      -c ${CLEAN_DIRS}
      -C default
      -d ${DOCKER_IMAGE}
      -e "deps/opm-tests/norne/norne-wells.pdf \
          deps/opm-tests/norne/norne-wells-noecl.pdf"
      -g "jenkins run norne norne_parallel with downstreams please"
      -o ${module}
      -r ${OPM_TESTS_LOCAL_ROOT}
      -R ${REPO_ROOT}
      -t run
      ${TOOLCHAIN}
  )
endforeach()

add_test(
  NAME
    update_data+opm-tests
  COMMAND
    ${PROJECT_SOURCE_DIR}/build.sh
    -b ${PROJECT_BINARY_DIR}
    -c ${CLEAN_DIRS}
    -C default
    -d ${DOCKER_IMAGE}
    -e data_diff
    -g "jenkins build this with downstreams failure_report update_data please"
    -n 2
    -o opm-tests
    -p ${PROJECT_SOURCE_DIR}/spe1_force_failures.patch
    -r ${OPM_TESTS_LOCAL_ROOT}
    -R ${REPO_ROOT}
    -t update_data
    ${TOOLCHAIN}
)

foreach(module opm-common opm-grid opm-upscaling)
  add_test(
    NAME
      post+${module}
    COMMAND
      ${PROJECT_SOURCE_DIR}/build.sh
      -b ${PROJECT_BINARY_DIR}
      -c ${CLEAN_DIRS}
      -C "default serial"
      -d ${DOCKER_IMAGE}
      -g "jenkins build this serial please"
      -o ${module}
      -r ${OPM_TESTS_LOCAL_ROOT}
      -R ${REPO_ROOT}
      -t post
      ${TOOLCHAIN}
  )
endforeach()

add_test(
  NAME
    post+opm-simulators
  COMMAND
    ${PROJECT_SOURCE_DIR}/build.sh
    -b ${PROJECT_BINARY_DIR}
    -c ${CLEAN_DIRS}
    -C "default hipify rocm serial"
    -d ${DOCKER_IMAGE}
    -e "deps/opm-tests/norne/norne-wells.pdf \
        deps/opm-tests/norne/norne-wells-noecl.pdf"
    -g "jenkins run norne norne_parallel serial rocm hipify please"
    -o opm-simulators
    -r ${OPM_TESTS_LOCAL_ROOT}
    -R ${REPO_ROOT}
    -t post
    ${TOOLCHAIN}
)
