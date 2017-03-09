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
Center = riGetActiveCellCenters();
CInfo = riGetActiveCellInfo();

value=Center(100,:)
CInfo(100,:)
printf ("Cell Indexes: %i %i %i \n", CInfo(100,2:4))
printf ("Cell Center : %9.2f %9.2f %9.2f \n", value(:))

