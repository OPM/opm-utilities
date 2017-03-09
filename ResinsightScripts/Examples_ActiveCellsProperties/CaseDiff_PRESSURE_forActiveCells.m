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

# Calculate the difference in Dynamic properties between two cases spesified order and write result back to case #2 
CaseNo(1)=1;			# Select case1, as case number loaded into ResInsight 
CaseNo(2)=2;			# Select case2
Case = riGetCases();
print=false;

# Choose parameter(s)
for P = {"PRESSURE"}		
	P1  = riGetActiveCellProperty(Case(CaseNo(1)).CaseId,P);	# Load case1 data
	P2  = riGetActiveCellProperty(Case(CaseNo(2)).CaseId,P);	# Load case2 data

	if all(size(P1)==size(P2))					# Check match of i,j,k dimension 
		DIFF_P = P1;
		DIFF_P = P2.-P1;					# Calculate diff = Case2 - Case1

		P_Name = ["DIFF_",P{1}];
		disp_txt = ["Wrote '",P_Name,"' to ",Case(CaseNo(2)).CaseName,...
			   ". This is ",P{1}," for ",Case(CaseNo(2)).CaseName," - " ,Case(CaseNo(1)).CaseName];
		disp(disp_txt)		
		riSetActiveCellProperty(DIFF_P,Case(CaseNo(2)).CaseId,P_Name);		# Write diff to case2
		print=true;
	else
		disp("Grid size mismatch  -  check input")
	end
end
if print
 	disp("New parameter(s) is put in the Cell Result ""Generated"" folder")
end
