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
# Move a grid property imported as ascii Input Paramater (.grdecl) into a Result Case
# Note! The Grid must have the same dimension for the Input Case as the Result Case.

# User input: 
#----------------------------------------------------------------------
GridNo      = 0;			# Select grid: Main grid = 0, LGRs = 1,2,..
InputCase   = 1;			# Select Input  case number - as number listed in the Project Tree.
ResultCase  = 1;			# Select Result case number - as number listed in the Project Tree.

# Specify one or multiple Input case properties. e.g. {"PERMX" "PERMZ" "PORO"}
PropInputNames = {"PERMX"};   	

# New property name in Result case
PropResultNames   = {"PERMX_grdecl1"};

#----------------------------------------------------------------------

Case = riGetCases();

# Find Input and Result cases in Project Tree
numInput   = 1;
numResult  = 1;

for i = 1 : length(Case)
 if strcmp(Case(i).CaseType,"InputCase");	
  InputId(numInput) = Case(i).CaseId;
  InputList(numInput) = i;  
  numInput++;
 
 elseif strcmp(Case(i).CaseType,"ResultCase");	
  ResultId(numInput) = Case(i).CaseId;
  ResultList(numInput) = i;
  numResult++;
 
 end
end

# Check for Input case present
if (InputCase > length(InputId))
 disp("")
 error("Not that many Input cases loaded - check your InputCase number! ");
end

# Check for Result case present
if (ResultCase > length(ResultId))
 disp("")
 error("Not that many Result cases loaded - check your ResultCase number! ");
end

# Loop for multiple  properties
i  = 1;

for P = PropInputNames		

	P1  = riGetGridProperty(InputId(InputCase), GridNo, P);				# Load Input case data

	riSetGridProperty(P1, ResultId(ResultCase), GridNo, PropResultNames{i}); 	# Write Input param to Result case

	disp(["=> Wrote '",PropResultNames{i},"' to case:  ",Case(ResultList(ResultCase)).CaseName, " / Cell Result / ""Generated"" "]);
	
	i = i + 1;	

end
