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
Days = riGetTimeStepDays();
CurrentCase = riGetCurrentCase();

% Print cell value vs time

for P = P_dynamic
 P1  = riGetGridProperty(GridNo,P{1});	# Load parameter
 [nx ny nx nts] = size(P1);

 % print values to screen
 printf('%s %s \n', P{}, CurrentCase.CaseName);   % Header - parameter and case name
 printf('%s %s %i %s %i %s %i %s \n', " Time(Days)  "," Cell (", Cell_I, ", ", Cell_J, ", " , Cell_K, ")");  % Header - table
   
 for ts=1:nts
  printf('%12.3f %12.3f \n', Days(ts), P1(Cell_I,Cell_J,Cell_K,ts)  );  % Print data
 end
  
end
