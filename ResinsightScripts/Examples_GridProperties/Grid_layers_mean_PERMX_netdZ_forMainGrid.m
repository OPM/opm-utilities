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

# Calculate arithmetric mean permeability weightet by net hight for all layers for active cells in main grid

GridNo=0;					# Main grid number = 0
# Get Static parameters from ResInsight
KX  = riGetGridProperty(GridNo,"PERMX");
DZ  = riGetGridProperty(GridNo,"DZ");
NG  = riGetGridProperty(GridNo,"NTG");
DIM = riGetGridDimensions();

netZ = NG.*DZ;					# Calculate net cell height
kh   = KX.*netZ;				# Calculate net cell kh
 
# Calculate arithmetric mean Kx net height weighted for all layers in main grid
KX2D_mean = sum(kh, 3)./sum(netZ, 3);		# Calulate 2-D array with average k-layers, K-dir is DIM=3
KX3D_mean = repmat(KX2D_mean, [1 1 DIM(3)]); 	# Copy/repeat 2-D array to 3-D array in K-direction (DIM=3) 

# Set result back into ResInsight
riSetGridProperty(KX3D_mean,GridNo,"PERMX_mean_weighted_netZ");
