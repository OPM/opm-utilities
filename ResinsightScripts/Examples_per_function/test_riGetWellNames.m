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


WellNames = riGetWellNames();
%fieldnames(WellNames)
size(WellNames)
disp("Variable WellNames = riGetWellNames")
WellNames

[n m]=size(WellNames);
cellWellNames={};
for i=1:n
	cellWellNames{i}=strtrim(WellNames(i,:));
end

TimeStep=2;
%WellName='Q-1H'
WellNames{1}

WellCellInfo=riGetWellCells(WellNames{1}, TimeStep);
disp("Variable WellCellInfo = riGetWellCells")
fieldnames(WellCellInfo)

[[WellCellInfo.I]' [WellCellInfo.J]' [WellCellInfo.K]' [WellCellInfo.GridIndex]' [WellCellInfo.CellStatus]' [WellCellInfo.BranchId]' [WellCellInfo.SegmentId]']

WellStatus=riGetWellStatus(WellNames{1});
disp("Variable WellStatus = riGetWellStatus")
fieldnames(WellStatus)

WellStatus.WellType
[WellStatus.WellStatus]'

%[[WellStatus.WellType]' [WellStatus.WellStatus]']


