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



# Calculate sum FIPOIL column hight for selected layers for main grid

# Define a set of zones with K1 K2 indexes
zones(1,:)=[ 1  9];	# Zone1 K1 K2 indexes
zones(2,:)=[10 19];
zones(3,:)=[20 29]	# Copy rows to add more zones, increase row index by 1

GridNo=0;							# Main grid number = 0
FIPOIL  = riGetGridProperty(GridNo,"FIPOIL");
DX   = riGetGridProperty(GridNo,"DX");
DY   = riGetGridProperty(GridNo,"DY");
DIM  = riGetGridDimensions();

[x y z ts] = size(FIPOIL);

CellArea = DX.*DY;
CellArea = max(CellArea, 0.000001);					# Ensure CellArea > 0 when used as denominator
for i = 1:ts								# For each time step
  FIPOIL(:,:,:,i) = FIPOIL(:,:,:,i)./CellArea(:,:,:);			# Change FIPOIL to oil column hight with dividing by cell area
endfor

SOIL3D_sum = FIPOIL;
RANGE = zeros(size(FIPOIL));

numZone=1;										
for k = zones'									# for each zone
 for i = 1:ts									# for each time step
  SOIL2D_sum = sum(FIPOIL(:,:,k(1):k(2),i), 3);					# Calulate 2-D array with average k-layers, K-dir is DIM=3
  SOIL3D_sum(:,:,k(1):k(2),i) = repmat(SOIL2D_sum, [1 1 (k(2)-k(1)+1)]); 	# Copy/repeat 2-D array to 3-D array in K-direction
 endfor
 RANGE(:,:,k(1):k(2)) = numZone;
 numZone++;
endfor
riSetGridProperty(SOIL3D_sum,GridNo,"FIPOILcolhight_per_zone");
riSetGridProperty(RANGE,GridNo,"Zones");					# Write Zones, numbering the ranges 1,2,3..

# Calculate the change in oil saturation with time compared to timestep 1
disp('Calculating time diff ...')
SOILDIFF = SOIL3D_sum;
for i=1:ts 
	FIPOILDIFF(:,:,:,i) = SOIL3D_sum(:,:,:,i) - SOIL3D_sum(:,:,:,1);
endfor
riSetGridProperty(FIPOILDIFF,GridNo,"FIPOILcolhight_per_zones_dt_DIFF");

