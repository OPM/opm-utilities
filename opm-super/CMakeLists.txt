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
add_subdirectory(opm-models)
add_dependencies(opm-models_prepare opmgrid)
set(BUILD_TESTING 1)

add_subdirectory(opm-simulators)
add_dependencies(opmsimulators opmgrid)
add_subdirectory(opm-upscaling)
add_dependencies(opmupscaling opmgrid)

add_dependencies(ebos_libblackoil opmcommon)
add_dependencies(flow_libblackoil opmcommon)

foreach(OBJ brine extbo energy foam gasoil gaswater oilwater oilwater_polymer polymer solvent)
  if(BUILD_EBOS_EXTENSIONS)
    add_dependencies(ebos_lib${OBJ} opmcommon)
  endif()
  add_dependencies(flow_lib${OBJ} opmcommon)
endforeach()

set(FLOW_OBJECTS oilwater_brine oilwater_polymer_injectivity)
if(BUILD_FLOW_POLY_GRID)
  list(APPEND FLOW_OBJECTS blackoil_poly)
endif()
if(FLOW_BUILD_VARIANTS)
  list(APPEND FLOW_OBJECTS onephase onephase_energy)
endif()
foreach(OBJ ${FLOW_OBJECTS})
  add_dependencies(flow_lib${OBJ} opmcommon)
endforeach()
