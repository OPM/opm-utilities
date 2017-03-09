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

# Find all dynamic properties

Prop = riGetPropertyNames();
numProp = rows(Prop);
numDynamic = 1;

# Find dynamic properties
for i=1:numProp
  if strcmp(Prop(i).PropType,"DynamicNative");	# 1 when equal "DynamicNative" properties
    P_dynamic(numDynamic) = {Prop(i).PropName};
    numDynamic++;
  endif
endfor

# Calculate difference from time step 1
for P = P_dynamic		
  P1  = riGetActiveCellProperty(P);	# Load parameter

  DIFF_P = P1;
  for i=1:columns(P1) 
    DIFF_P(:,i) = P1(:,i) - P1(:,1);
  endfor

  P_Name = ["Diff_dt_",P{1}];
  riSetActiveCellProperty(DIFF_P,P_Name);
end
