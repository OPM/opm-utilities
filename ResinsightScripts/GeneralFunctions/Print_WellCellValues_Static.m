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
GridNo=0;	% Main grid number = 0
DIM  = riGetGridDimensions();
Days = riGetTimeStepDays();
CurrentCase = riGetCurrentCase();

WellNames = riGetWellNames();
wellCells = riGetWellCells(wellName{}, wellTimeStep);
[N n] = size (wellCells);

for i=1:N
 Cell(i,1) = wellCells(i).I;
 Cell(i,2) = wellCells(i).J;
 Cell(i,3) = wellCells(i).K;
end 
   


% Print cell value for each well connection

for P = P_static
 P1  = riGetGridProperty(GridNo,P{1});	# Load parameter
 [nx ny nx nts] = size(P1);

 % print values to screen
 printf('%s %s \n', "Simulation:", CurrentCase.CaseName);   % Header -  case name
 printf('%12s %15s \n', wellName{}, P{});   % Header - well and parameter
 
 for i=1:rows(Cell)
  printf('%s%s%s  ', "(", num2str (Cell (i,:)), ")" );   % Header: Cell indexes
  printf('%14.3f', P1(Cell(i,1),Cell(i,2),Cell(i,3), 1)  );  % Print cell values 
  printf(' \n') 
 end
  
end
