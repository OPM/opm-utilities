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

# Test of riGetGridProperty & riSetGridProperty for a Static parameter
GridNo=0;					# Main grid number = 0
tic()
KX  = riGetGridProperty(GridNo,"PERMX");	# Load Static parameters
ACT  = riGetGridProperty(GridNo,"ACTNUM");
DIM = riGetGridDimensions();
toc()
# Calculate arithmetric mean permeability for all layers for active cells in main grid
KX2D_mean = sum(KX, 3)./sum(ACT, 3);		# Calulate 2-D array with average k-layers, K-dir is DIM=3, SumKxInLayer/SumActiveCellsInLayer  
KX3D_mean = repmat(KX2D_mean, [1 1 DIM(3)]); 	# Copy/repeat 2-D array to 3-D array in K-direction, NZ=DIM(3) 
toc()
riSetGridProperty(KX3D_mean,GridNo,"PERMX_MEAN"); # Write result back to ResInsight for Main grid=0
toc()
# --------------------------------------------------------------
# Test of Dynamic parameter
tic()
SOIL_ALL = riGetGridProperty(GridNo,"SOIL_dt_DIFF");		# Load Dynamic parameter with all time steps:
toc
SOIL_ALL=SOIL_ALL.*2;
size(SOIL_ALL)
toc
riSetGridProperty(SOIL_ALL,GridNo,"SOIL_all_ts");   	# Write result back to ResInsight for all time steps
toc

# ---------------------------------------------------------------
# Test of Dynamic parameter
disp("test 6 dynamic ts")
ts = [1:10]; 				# Selected timesteps - Optional input
toc()
SOIL = riGetGridProperty(GridNo,"SOIL",ts);	# Load Dynamic parameter with selected time steps:
toc()
#size(SOIL)
disp("Multiply SOIL by 2")
SOIL=SOIL.*2;
toc()
riSetGridProperty(SOIL,GridNo,"SOIL_selected_ts10",ts);  # Write result back to ResInsight for selected timesteps
toc()
