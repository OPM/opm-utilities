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
# Make a binary parameter based on a cut-off value
# Inactave cells are included in freqency calculation (as 0)

CutOff = 0.15
PropName = ("PORO")


# Find CaseType "ResultCase" 
Cases = riGetCases();
numCase = rows(Cases);
caseListId = [];
numListId = 1;

for i = 1 : numCase

  if ( strcmp(Cases(i).CaseType,"ResultCase") );		# true when match case type 
   caseListId(numListId) = Cases(i).CaseId;
   numListId++;
  endif

endfor

for i = 1 : columns(caseListId)

 Param  = riGetGridProperty(caseListId(i),0,PropName);		# read parameter from ResInsight
 Binary = ( Param >= CutOff );

 if (i == 1)
  SumBinary = Binary;
 else
  SumBinary = SumBinary .+ Binary;
 end
 
end

MeanBinary = SumBinary ./ columns(caseListId);			# Normalize on N cases

riSetGridProperty(MeanBinary,caseListId(1),0,"MeanBinary");	# return parameter to ResInsights first case in list






