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

# Calculate arithmetric mean permeability for all layers for active cells in main grid
# Script re-written to aviod time consuming for-loops over I and J indexes.

BOX = (CInfo(:,1) == 0);			# Checks for Main grid = 0
C=CInfo(BOX,:);					# CInfo with starting point 1,1,1 for I/J/K
C_index = C(:,2)+DIM(1)*(C(:,3)-1)+DIM(1)*DIM(2).*(C(:,4)-1);		# Calculate cell index no. in a 3-D array

KX3D = zeros(DIM(1), DIM(2), DIM(3));		# Create 3-D array
ACT3D = KX3D;
KX3D(C_index) = PERMX(BOX);			# Put active cell data into 3-D array for Main grid
ACT3D(C_index) = 1;				# Define active cells in 3-D array

KX2D_avg = sum(KX3D, 3)./sum(ACT3D, 3);		# Calulate 2-D array with average k-layers, DIM=3  
KX3D_avg = repmat(KX2D_avg, [1 1 DIM(3)]); 	# Copy 2-D array to 3-D array in K-direction
KX_AVG = PERMX*NaN;
KX_AVG(BOX) = KX3D_avg(C_index);		# Copy active cell in 3-D array to 1-D array

riSetActiveCellProperty(KX_AVG, "KX_AVG");

