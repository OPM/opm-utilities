project(opm)

cmake_minimum_required(VERSION 2.8)

foreach(TARGET opm-common opm-parser opm-output opm-material opm-grid
               opm-models opm-simulators opm-upscaling)
  set(${TARGET}_DIR ${CMAKE_BINARY_DIR}/${TARGET})
endforeach()

set(SIBLING_SEARCH 0)
# Necessary, sadly this means no IDE project generation
set_property(GLOBAL PROPERTY ALLOW_DUPLICATE_CUSTOM_TARGETS 1)

enable_testing()
add_subdirectory(opm-common)
add_subdirectory(opm-material)
add_dependencies(opm-material_prepare opmcommon)
add_subdirectory(opm-grid)
add_dependencies(opmgrid opmcommon)

# To not build unrelated "tests" in opm-models unless requested
set(BUILD_TESTING 0)
# To not add disabled tests to the ctest list
set(ADD_DISABLED_CTESTS 0)
add_subdirectory(opm-models)
add_dependencies(opm-models_prepare opmgrid)
set(BUILD_TESTING 1)

add_subdirectory(opm-simulators)
add_dependencies(opmsimulators opmgrid)
add_subdirectory(opm-upscaling)
add_dependencies(opmupscaling opmgrid)
