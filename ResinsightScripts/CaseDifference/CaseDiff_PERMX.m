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

# Calculate the difference in properties between two spesified cases and write result back to case #2

# User selection: 
#----------------------------------------------------------------------
GridNo    = 0;			# Select grid: Main grid = 0, LGRs = 1,2,..
CaseNo(1) = 1;			# Select 1st case for diff, from 1 in the order the cases are listed in ri tree-structure. 
CaseNo(2) = 2;			# Select 2nd case for diff
PropNames = {"PERMX"};   	# Specify one or multiple Result properties. e.g. {"SOIL" "PRESSURE"}
#----------------------------------------------------------------------

Case = riGetCases();

# Check for real case input number
if (min(CaseNo) < 1)
 disp("")
 error("Minimum Case selection number is 1 - check your CaseNo() input! ");
end
if (max(CaseNo) > numel([Case.CaseId]))
 disp("")
 error("Not that many cases loaded - check your CaseNo() input! ");
end


# Loop for multiple Result properties
for P = PropNames		
	P1  = riGetGridProperty(Case(CaseNo(1)).CaseId, GridNo, P);	# Load case1 data
	P2  = riGetGridProperty(Case(CaseNo(2)).CaseId, GridNo, P);	# Load case2 data

	if all(size(P1)==size(P2))					# Check match of i,j,k,ts dimension 
		DIFF_P = P1;
		DIFF_P = P2.-P1;					# Calculate diff = Case2 - Case1		
	        DiffName = ["DIFF_",P{1}];

		riSetGridProperty(DIFF_P, Case(CaseNo(2)).CaseId, GridNo, DiffName);	# Write diff to case2

		disp([" Calculated ",P{1}," difference: ",Case(CaseNo(2)).CaseName," - " ,Case(CaseNo(1)).CaseName]);
		disp([" Wrote '",DiffName,"' to case:  ",Case(CaseNo(2)).CaseName, ", to the Cell Result ""Generated"" folder."]);
	else
		error(" Grid size mismatch  -  check input")
	end
end
