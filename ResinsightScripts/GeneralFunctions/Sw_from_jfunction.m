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

DEPTH = riGetActiveCellProperty("DEPTH");
KX = riGetActiveCellProperty("PERMX");
PORO = riGetActiveCellProperty("PORO");
#SWAT1 = riGetActiveCellProperty("SWATINIT");

# Set depth for Free Water Level (FWL)
FWL = 4055;
 
# === Exampel calculate Swirr ====
idx=find((KX>0));	% find cells with positive values
SWI = ones(size(KX));
SWI = (KX<=0)*0.25;			   % else: KX equal 0 or less
SWI(idx) = 0.31-0.079*log10(KX(idx)); % if: KX positive 

# === Exampel calculate Sw from a empirical J-function
HHC=max(0.001,FWL-DEPTH);  % Calculated hight of oil column, min 0.001 to avoid neg. values

R=zeros(size(PORO));
idx=find((KX>0) & (PORO>0));	% find cells with positive values
R(idx) = sqrt(KX(idx)./PORO(idx));
R = max(0.0000001,R);

SWJ = ones(size(PORO));
SWJ = (HHC/2.6.*R).^(-1/3.88);   % J-function: Swj=h/2.6*sqrt(kx/phi))^(-1/3.88)
SWJ = min(1,SWJ);		 % Remove Sw > 1

# Check consistent SWI < SWJ
#idx2 = find((SWJ-SWI)<=0);
#SWI(idx2) = SWJ(idx2) - 0.01;	% For Swi > Swj, Swi is set 0.01 below Swj

# Diff QC
#SWJ_diff=SWJ-SWAT1;

riSetActiveCellProperty(SWI, "SWI");
riSetActiveCellProperty(SWJ, "SWJ");
#riSetActiveCellProperty(SWJ_diff, "SWJ_diff");
