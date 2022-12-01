project(opm)

cmake_minimum_required(VERSION 3.5)

foreach(TARGET opm-common opm-grid opm-models opm-simulators opm-upscaling)
  set(${TARGET}_DIR ${CMAKE_BINARY_DIR}/${TARGET})
endforeach()

set(SIBLING_SEARCH 0)
# Necessary, sadly this means no IDE project generation
set_property(GLOBAL PROPERTY ALLOW_DUPLICATE_CUSTOM_TARGETS 1)

enable_testing()
add_subdirectory(opm-common)
add_subdirectory(opm-grid)
add_dependencies(opmgrid opmcommon)
add_subdirectory(opm-models)
add_dependencies(opm-models_prepare opmgrid)
add_subdirectory(opm-simulators)
add_dependencies(opmsimulators opmgrid)
add_subdirectory(opm-upscaling)
add_dependencies(opmupscaling opmgrid)

set(FLOW_OBJECTS blackoil brine energy extbo foam gasoil gaswater
                 oilwater oilwater_brine gaswater_brine oilwater_polymer
                 oilwater_polymer_injectivity micp polymer solvent
                 gasoil_energy brine_saltprecipitation
                 gaswater_saltprec_vapwat brine_precsalt_vapwat
                 blackoil_legacyassembly gasoildiffuse)
if(BUILD_FLOW_POLY_GRID)
  list(APPEND FLOW_OBJECTS blackoil_poly)
endif()
if(FLOW_BUILD_VARIANTS)
  list(APPEND FLOW_OBJECTS brine_energy onephase onephase_energy)
endif()
foreach(OBJ ${FLOW_OBJECTS})
  add_dependencies(flow_lib${OBJ} opmcommon)
endforeach()
