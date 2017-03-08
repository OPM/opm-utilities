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


PERMX = riGetActiveCellProperty("PERMX");
CInfo = riGetActiveCellInfo();
DIM = riGetMainGridDimensions();

# Calculate arithmetric mean permeability for selected layers for active cells in main grid
# Script re-written to avoid time consuming for-loops over I and J indexes.

# Define a set of zones with K1 K2 indexes and calculated mean PERMX for each zone
zones(1,:)=[17 18];	# Zone1 K1 K2 indexes
zones(2,:)=[20 22];	# Copy rows to add more zones, increase row index by 1


BOX = (CInfo(:,1) == 0);			# Checks for Main grid = 0
C=CInfo(BOX,:);					# CInfo with starting point 1,1,1 for I/J/K
C_index = C(:,2)+DIM(1)*(C(:,3)-1)+DIM(1)*DIM(2).*(C(:,4)-1);		# Calculate cell index no. in a 3-D array

KX3D = zeros(DIM(1), DIM(2), DIM(3));		# Create 3-D array
ACT3D = KX3D;
RANGE = KX3D;
KX3D(C_index) = PERMX(BOX);			# Put active cell data into 3-D array
ACT3D(C_index) = 1;				# Define active cells in 3-D array
PAR_3D_avg = KX3D;				# Define result matrix size
i=1;

for k = zones'
  PAR_2D_avg = sum(KX3D(:,:,k(1):k(2)), 3)./sum(ACT3D(:,:,k(1):k(2)), 3);	# Calulate 2-D array with average k-layers, DIM=3  
  PAR_3D_avg(:,:,k(1):k(2)) = repmat(PAR_2D_avg, [1 1 (k(2)-k(1)+1)]); 		# Copy 2-D array to 3-D array in K-direction for selected k-layers
  RANGE(:,:,k(1):k(2)) = i;
  i++;
endfor

PAR_AVG = PERMX*NaN;					# Define result vector and set NaN to identify LGR-data.
RANGE1D = PERMX*NaN;
PAR_AVG(BOX) = PAR_3D_avg(C_index);			# Copy active cell in 3-D array to 1-D array
RANGE1D(BOX) = RANGE(C_index);			

riSetActiveCellProperty(PAR_AVG, "KX_avg_zones");	# Write to ri
riSetActiveCellProperty(RANGE1D, "Zones");		# Write Zones, numbering the ranges 1,2,3..
