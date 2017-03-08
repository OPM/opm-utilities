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

ts=[1:10];
SOIL = riGetActiveCellProperty("SOIL",ts);
CInfo = riGetActiveCellInfo();
DIM = riGetGridDimensions();

# Calculate arithmetric mean SOIL for zone layers for active cells in main grid
# Script re-written to avoid time consuming for-loops over I and J indexes.

# Define a set of zones from K1 to K2 indexes and calculated mean SOIL for each zone
zones(1,:)=[ 50  52];	# Zone1 K1 K2 indexes
zones(2,:)=[90  119];	# Copy rows to add more zones, increase row index by 1
zones(3,:)=[120 143];	# Copy rows to add more zones, increase row index by 1
%zones(2,:)=[ 23  24];	

BOX = (CInfo(:,1) == 0);			# Checks for Main grid = 0
C=CInfo(BOX,:);					# CInfo with starting point 1,1,1 for I/J/K
DIM=DIM';					# Array bug for riGetGridDimensions?

C_index = C(:,2)+DIM(1)*(C(:,3)-1)+DIM(1)*DIM(2).*(C(:,4)-1);		# Calculate cell index no. in a 3-D array

PAR_4D = zeros(DIM(1), DIM(2), DIM(3), columns(SOIL));		# Create 4-D array (NX NY NZ ts)
ACT_4D = PAR_4D;

C_index_4D=[];
for ts=1:columns(SOIL)
  C_index_4D=[C_index_4D C_index+DIM(1)*DIM(2)*DIM(3)*(ts-1)];	# Create 4-D array cell index no.
endfor

PAR_4D(C_index_4D) = SOIL(BOX,:);		# Put active cell data into 4-D array
ACT_4D(C_index_4D) = 1;				# Define active cells in 4-D array
PAR4D_avg = PAR_4D;				# Define size and default values for result

i=1;
for k = zones'
  PAR3D_avg = sum(PAR_4D(:,:,k(1):k(2),:), 3)./sum(ACT_4D(:,:,k(1):k(2),:), 3);	# Calulate 2-D array with average k-layers, DIM=3  
  PAR4D_avg(:,:,k(1):k(2),:) = repmat(PAR3D_avg, [1 1 (k(2)-k(1)+1) 1]); 	# Copy 2-D array to 3-D array in K-direction for selected k-layers
  RANGE(:,:,k(1):k(2)) = i;
  i++;
endfor

PAR_AVG = SOIL*NaN;
PAR_AVG(1:length(C_index),:) = PAR4D_avg(C_index_4D);	# Copy active cell in 4-D array to 2-D array
	

riSetActiveCellProperty(PAR_AVG, "SOIL_zone_mean");	# Write to ri
#riSetActiveCellProperty(RANGE1D, "Zones");		# Write Zones, numbering the ranges 1,2,3..


# Calculate the change in oil saturation with time compared to timestep 1
SOILDIFF = PAR_AVG;
for i=1:columns(PAR_AVG) 
	SOILDIFF(:,i) = PAR_AVG(:,i) - PAR_AVG(:,1);
endfor

riSetActiveCellProperty(SOILDIFF, "SOIL_avg_dt_DIFF",ts);
