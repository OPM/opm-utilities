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

SOIL = riGetActiveCellProperty("SOIL");
CInfo = riGetActiveCellInfo();
DIM = riGetMainGridDimensions();

# Calculate arithmetric mean permeability for all layers for active cells in main grid
# Script re-written to avoid time consuming for-loops over I and J indexes.

BOX = (CInfo(:,1) == 0);			# Checks for Main grid = 0
C=CInfo(BOX,:);					# CInfo with starting point 1,1,1 for I/J/K
C_index = C(:,2)+DIM(1)*(C(:,3)-1)+DIM(1)*DIM(2).*(C(:,4)-1);		# Calculate cell index no. in a 3-D array

PAR_4D = zeros(DIM(1), DIM(2), DIM(3), columns(SOIL));		# Create 4-D array (NX NY NZ ts)
ACT_4D = PAR_4D;

C_index_4D=[];
for ts=1:columns(SOIL)
  C_index_4D=[C_index_4D C_index+DIM(1)*DIM(2)*DIM(3)*(ts-1)];	# Create 4-D array cell index no.
endfor

PAR_4D(C_index_4D) = SOIL(BOX,:);		# Put active cell data into 4-D array
ACT_4D(C_index_4D) = 1;				# Define active cells in 4-D array

PAR3D_avg = sum(PAR_4D, 3)./sum(ACT_4D, 3);	# Calulate 2-D array with average k-layers, DIM=3  
PAR4D_avg = repmat(PAR3D_avg, [1 1 DIM(3) 1]); 	# Copy 2-D array to 3-D array in K-direction
PAR_AVG = SOIL*NaN;
PAR_AVG(1:length(C_index),:) = PAR4D_avg(C_index_4D);	# Copy active cell in 3-D array to 1-D array

riSetActiveCellProperty(PAR_AVG, "SOIL_AVG");

