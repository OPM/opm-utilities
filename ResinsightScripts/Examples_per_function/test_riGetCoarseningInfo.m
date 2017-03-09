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

# Retrive data from ResInsight
CInfo = riGetCoarseningInfo();

CInfo(:,:)

# Defining start and end I-, J- and K-index for each coarse box
I1_INDEX = CInfo(:,1);
I2_INDEX = CInfo(:,2);
J1_INDEX = CInfo(:,3);
J1_INDEX = CInfo(:,4);
J1_INDEX = CInfo(:,5);
J1_INDEX = CInfo(:,6);

