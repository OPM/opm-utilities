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


# Calculate arithmetric mean permeability weightet by net height for selected layers in main grid

GridNo=0;					# Main grid number = 0
# Define a set of zones with K1 K2 indexes and calculated mean PERMX for each zone
zones(1,:)=[17 18];	# Zone1 K1 K2 indexes
zones(2,:)=[20 22];	# Copy rows to add more zones, increase row index by 1

# Get Static parameters from ResInsight
KX  = riGetGridProperty(GridNo,"PERMX");
DZ  = riGetGridProperty(GridNo,"DZ");
NG  = riGetGridProperty(GridNo,"NTG");
DIM = riGetGridDimensions();

netZ = NG.*DZ;					# Calculate net cell height
kh   = KX.*netZ;				# Calculate net cell kh
KX3D_mean = KX;
RANGE = zeros(size(KX));

i=1;										# Numbering the zones
for k = zones'									# Loop over zones
  KX2D_mean = sum(kh(:,:,k(1):k(2)), 3)./sum(netZ(:,:,k(1):k(2)), 3);		# Calulate 2-D array for k-layers, K-dir is DIM=3
  KX3D_mean(:,:,k(1):k(2)) = repmat(KX2D_mean, [1 1 (k(2)-k(1)+1) 1]); 		# Copy/repeat 2-D array to 3-D array for relevant k-layers (DIM=3) 
  RANGE(:,:,k(1):k(2)) = i;
  i++;
endfor

# Set result back into ResInsight
riSetGridProperty(KX3D_mean,GridNo,"PERMX_mean_weighted_netZ");
riSetGridProperty(RANGE,GridNo,"Zones");					# Write Zones, numbering the ranges 1,2,3..
