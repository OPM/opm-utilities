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


# Calculate  mean SOIL weighted by PV for all layers for main grid

GridNo=0;							# Main grid number = 0
SOIL  = riGetGridProperty(GridNo,"SOIL");
PORV  = riGetGridProperty(GridNo,"PORV");
DIM = riGetGridDimensions();

[x y z ts] = size(SOIL);

for i=1:ts							# for each time step:
  SOILPV = SOIL(:,:,:,i).*PORV(:,:,:);				# Calculate oil volume in Rm3 per cell

  # Calculate arithmetric mean So weighted by pore volume for all layers in main grid
  SOIL2D_mean = sum(SOILPV, 3)./sum(PORV, 3);			# Calulate 2-D array with average k-layers, K-dir is DIM=3
  SOIL3D_mean(:,:,:,i) = repmat(SOIL2D_mean, [1 1 DIM(3)]); 	# Copy/repeat 2-D array to 3-D array in K-direction
endfor
riSetGridProperty(SOIL3D_mean,GridNo,"SOIL_MeanByPV");


# Calculate the change in oil saturation with time compared to timestep 1
SOILDIFF = SOIL3D_mean;
for i=1:ts 
	SOILDIFF(:,:,:,i) = SOIL3D_mean(:,:,:,i) - SOIL3D_mean(:,:,:,1);
endfor
riSetGridProperty(SOILDIFF,GridNo,"SOIL_MeanByPV_dt_DIFF");
