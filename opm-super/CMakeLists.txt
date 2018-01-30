project(opm)

cmake_minimum_required(VERSION 2.8)

foreach(TARGET opm-common opm-parser opm-output opm-material opm-grid
               ewoms opm-simulators opm-upscaling)
  set(${TARGET}_DIR ${CMAKE_BINARY_DIR}/${TARGET})
endforeach()

set(SIBLING_SEARCH 0)
# Necessary, sadly this means no IDE project generation
set_property(GLOBAL PROPERTY ALLOW_DUPLICATE_CUSTOM_TARGETS 1)

enable_testing()
add_subdirectory(opm-common)
add_subdirectory(opm-parser)
add_dependencies(opmparser ecl opmcommon)
add_subdirectory(opm-output)
add_dependencies(opmoutput opmparser)
add_subdirectory(opm-material)
add_dependencies(opm-material_prepare opmparser)
add_subdirectory(opm-grid)
add_dependencies(opmgrid opmparser)

# To not build unrelated "tests" in ewoms unless requested
set(BUILD_TESTING 0)
# To not add disabled tests to the ctest list
set(ADD_DISABLED_CTESTS 0)
add_subdirectory(ewoms)
add_dependencies(ewoms_prepare opmgrid opmoutput)
set(BUILD_TESTING 1)

add_subdirectory(opm-simulators)
add_dependencies(opmsimulators opmgrid)
add_subdirectory(opm-upscaling)
add_dependencies(opmupscaling opmgrid)