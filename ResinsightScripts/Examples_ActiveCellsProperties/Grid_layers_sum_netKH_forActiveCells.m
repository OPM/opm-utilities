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
DIM = riGetMainGridDimensions();
DZ = riGetActiveCellProperty("DZ");
NTG = riGetActiveCellProperty("NTG");
CInfo = riGetActiveCellInfo();

# Calculate arithmetric mean permeability weightet by net hight for all layers for active cells in main grid

HNET=DZ.*NTG;					# Calculate net cell hight
KH = PERMX.*HNET;				# Calculate net kh

BOX = (CInfo(:,1) == 0);			# Checks for Main grid = 0
C=CInfo(BOX,:);					# Cell info with starting point 1,1,1 for I/J/K
C_index = C(:,2)+DIM(1)*(C(:,3)-1)+DIM(1)*DIM(2).*(C(:,4)-1);	# Calculate cell index no. in a 3-D array for main grid

PAR_3D = zeros(DIM(1), DIM(2), DIM(3));		# Create 3-D array with zeroes
PAR_3D(C_index) = KH(BOX);			# Put active cell data into 3-D array

PAR2D_sum = sum(PAR_3D, 3);			# Calulate 2-D array with average k-layers, DIM=3  
PAR3D_sum = repmat(PAR2D_sum, [1 1 DIM(3)]); 	# Copy 2-D array to 3-D array in K-direction
PAR_sum = PERMX*NaN;
PAR_sum(BOX) = PAR3D_sum(C_index);		# Copy active cell in 3-D array to 1-D array

riSetActiveCellProperty(PAR_sum, "netKH");	# Export to ri with proper name

