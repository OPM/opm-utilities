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


CInfo = riGetActiveCellInfo();
PERMX = riGetActiveCellProperty("PERMX");

# Copy PERMX cell values from one grid box to another grid box with SAME Size And Number Of Active Cells

# Define boxes to copy from/to with I1 I2 J1 J2 K1 K2 indexes
boxes(1,:)=[30 40 40 50 18 19];    % Copy data from Box1 I1 I2 J1 J2 K1 K2 indexes
boxes(2,:)=[30 40 60 70 21 22];	 % Copy data to Box2

PERMXAVG=PERMX;
RANGE=PERMX*0;
i=1;

ijk = boxes(1,:);
  # Checks for Main grid = 0, 
  BOX_FROM = find((CInfo(:,1) == 0)...					
      & (CInfo(:,2) >= ijk(1)) & (CInfo(:,2) <= ijk(2))...  % I1-I2
      & (CInfo(:,3) >= ijk(3)) & (CInfo(:,3) <= ijk(4))...  % J1-J2
      & (CInfo(:,4) >= ijk(5)) & (CInfo(:,4) <= ijk(6)));   % K1-K2
  RANGE(BOX_FROM) = i;

ijk = boxes(2,:);
  # Checks for Main grid = 0, 
  BOX_TO = find((CInfo(:,1) == 0)...					
      & (CInfo(:,2) >= ijk(1)) & (CInfo(:,2) <= ijk(2))...  % I1-I2
      & (CInfo(:,3) >= ijk(3)) & (CInfo(:,3) <= ijk(4))...  % J1-J2
      & (CInfo(:,4) >= ijk(5)) & (CInfo(:,4) <= ijk(6)));   % K1-K2

  PERMX(BOX_TO) = PERMX(BOX_FROM);
  i++;
  RANGE(BOX_TO) = i;

riSetActiveCellProperty(PERMX, "PERMX");
riSetActiveCellProperty(RANGE, "GRIDBOX");			% Write GRIDBOX, numbering the ranges 1,2,3..


