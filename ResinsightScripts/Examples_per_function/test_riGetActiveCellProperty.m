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


# Static parameter
tic()
PERMX = riGetActiveCellProperty("PERMX");
toc()
size(PERMX)
toc()
riSetActiveCellProperty(PERMX,"PERMX_TEST");
toc()
PERMX2 = PERMX.*2;
toc()
riSetActiveCellProperty(PERMX2,"PERMX_TESTX2");
toc()
# Dynamic parameter for list of selected time steps
TS=[1:6];
SOIL = riGetActiveCellProperty("SOIL",TS);
toc()
size(SOIL)
toc()
riSetActiveCellProperty(SOIL,"SOIL_TEST_6TS",TS);
toc()

fprintf (stderr, "10sec pause...\n");
 pause (10);

# Dynamic parameter for all time steps
tic()
SOIL = riGetActiveCellProperty("SOIL");
toc()
size(SOIL)
toc()
riSetActiveCellProperty(SOIL,"SOIL_TEST_ALL_ts");
toc()
SOILX2 = SOIL.*2;
toc()
riSetActiveCellProperty(SOILX2,"SOIL_TEST_X2");
toc()
size(SOIL)
