#  Copyright 2017 Statoil ASA.
#
#  This file is part of The Open Porous Media project (OPM).
#
#  OPM is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  OPM is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with OPM.  If not, see <http://www.gnu.org/licenses/>.
#
#  hhgs@statoil.com


# Retrive data from ResInsight
CInfo = riGetActiveCellInfo();

CInfo(1,:)

# Defining Grid index: The index of the grid the cell resides in. (Main grid has index 0) 
GRID_IDX = CInfo(:,1);

# Defining I-, J- and K-index for a grid.
I_INDEX = CInfo(:,2);
J_INDEX = CInfo(:,3);
K_INDEX = CInfo(:,4);

# Defining ParentGridIdx: 	The index to the grid that this cell's grid is residing in.
PGRID_IDX = CInfo(:,5);

# Defining PI, PJ, PK:  1-based address of the parent grid cell that this cell is a part of.
PI_INDEX = CInfo(:,6);
PJ_INDEX = CInfo(:,7);
PK_INDEX = CInfo(:,8);

# Defining CoarseBoxIdx: 1-based coarsening box index, -1 if none. 
CGRID_IDX = CInfo(:,9); 

# Write data to ResInsight
riSetActiveCellProperty(GRID_IDX, "Grid_Idx");
riSetActiveCellProperty(I_INDEX, "I_Index");
riSetActiveCellProperty(J_INDEX, "J_Index");
riSetActiveCellProperty(K_INDEX, "K_Index");
riSetActiveCellProperty(PGRID_IDX, "PGrid_Idx");
riSetActiveCellProperty(PI_INDEX, "PI_Index");
riSetActiveCellProperty(PJ_INDEX, "PJ_Index");
riSetActiveCellProperty(PK_INDEX, "PK_Index");
riSetActiveCellProperty(CGRID_IDX, "CGrid_Idx");

