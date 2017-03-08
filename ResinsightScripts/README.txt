This folder contains examples on Octave scripts for ResInsight.

The properties are available in two ways:
 2D-arrays (active_cells,ts) from the functions riGetActiveCellProperty and riSetActiveCellProperty
 4D-arrays (I,J,K,ts)	     from the functions riGetGridProperty	and riSetGridProperty.


For doing calulation on cell level for the hole grid, 
--> the 2D-arrays are most efficient and it includes any LGR

For doing calulation in I-, J- or K-direction,
--> the 4D-arrays are much simpler to use for I,J,K indexing. But the array only address one grid at a time.

--------------------------------------------------------------------------------------------------------------------

For a standalone Octave session working with ResInsight data,
  -> in the script, set "addpath" to find the ResinsightScripts-functions (and to script folder if needed)

addpath("/path/to/resinsight/installation");


