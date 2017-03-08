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


# Copy PERMX cell values from one grid box to another grid box
# Define to and from box I1 I2 J1 J2 K1 K2 range
fromBox(1,:) = [30 40 40 50 17 17];	% Box 1 copy from
fromBox(2,:) = [30 40 40 50 20 20];	% Box 2 copy from
toBox(1,:)   = [30 40 60 70 17 17];	% Box 1 copy to
toBox(2,:)   = [30 40 60 70 20 20];	% Box 2 copy to 

GridNo = 0;					# Main grid number = 0
KX = riGetGridProperty(GridNo,"PERMX");		# Get Static parameters from ResInsight

RANGE=zeros(size(KX));
BoxNo=1;

for i = 1:rows(fromBox)
  KX(toBox(i,1):toBox(i,2),toBox(i,3):toBox(i,4),toBox(i,5):toBox(i,6))=KX(fromBox(i,1):fromBox(i,2),fromBox(i,3):fromBox(i,4),fromBox(i,5):fromBox(i,6));
  RANGE(toBox(i,1):toBox(i,2),toBox(i,3):toBox(i,4),toBox(i,5):toBox(i,6))=BoxNo;
  BoxNo++;
endfor

riSetGridProperty(KX,GridNo,"PERMX");		# Set result back into ResInsight
riSetGridProperty(RANGE,GridNo,"Copy_Range");

disp ("New parameters are put in the Cell Result ""Generated"" folder")
