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

# Calculate the difference in STATIC properties between FINE and COARSE grid cases and write result back to case #2
# Cross plot average properties of FINE scale grid vs COARSE scale grid

# User selection: 
#----------------------------------------------------------------------
GridNo    = 0;			# Select grid: Main grid = 0, LGRs = 1,2,..
CaseNo(1) = 1;			# Select 1st case for diff, from 1 in the order the cases are listed in ri tree-structure. 
CaseNo(2) = 2;			# Select 2nd case for diff
PropNames = {"PERMX" "PORO"};   	# Specify one or multiple Result properties. e.g. {"SOIL" "PRESSURE"}
AllCells  = true;

FineCellDist = false;
Cells(1,:) = [ 3 2 2 ];
Cells(2,:) = [ 4 3 3 ];
print_hist_to_file = true;
numBin 	   = 10;

#----------------------------------------------------------------------
close all
numFig = 1;
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
#-------------------------

# Check for grid dimentions
GridDim1 = riGetGridDimensions(Case(CaseNo(1)).CaseId);
GridDim2 = riGetGridDimensions(Case(CaseNo(2)).CaseId);

NumEl1 = GridDim1(1,1).*GridDim1(1,2).*GridDim1(1,3);
NumEl2 = GridDim2(1,1).*GridDim2(1,2).*GridDim2(1,3);

if ( NumEl1 > NumEl2 )
 GridRatio(1) = GridDim1(1,1)./ GridDim2(1,1);
 GridRatio(2) = GridDim1(1,2)./ GridDim2(1,2);
 GridRatio(3) = GridDim1(1,3)./ GridDim2(1,3);
elseif  ( NumEl2 > NumEl1 )
 GridRatio(1) = GridDim1(1,1)./ GridDim2(1,1);
 GridRatio(2) = GridDim1(1,2)./ GridDim2(1,2);
 GridRatio(3) = GridDim1(1,3)./ GridDim2(1,3);
 # Change grid order to Fine Scale = 1st and Coarse = 2nd
 tmp = CaseNo(2);
 CaseNo(2) = CaseNo(1);
 CaseNo(1) = tmp;
 tmp = GridDim2;
 GridDim2 = GridDim1;
 GridDim1 = tmp;
else
 error("Compared Grids have same Size - check the case input! ");
end 

#----------------------------------------------------------------------------------------
# Loop for multiple Result properties
for P = PropNames		
 P1  = riGetGridProperty(Case(CaseNo(1)).CaseId, GridNo, P);	# Load Fine Scale data
 P2  = riGetGridProperty(Case(CaseNo(2)).CaseId, GridNo, P);	# Load Coarse Scale data

 if AllCells
  MeanFine = zeros(size(P2));
  SumFine  = MeanFine;
  
  for i = 1 : GridDim2(1,1)
   for j = 1 : GridDim2(1,2)
    for k = 1 : GridDim2(1,3)  
     i1 = GridRatio(1).* ( i - 1) + 1;
     i2 = GridRatio(1).*   i;
     j1 = GridRatio(2).* ( j - 1) + 1;
     j2 = GridRatio(2).*   j;
     k1 = GridRatio(3).* ( k - 1) + 1;
     k2 = GridRatio(3).*   k;
     
     MeanFine(i,j,k) = mean(P1(i1:i2,j1:j2,k1:k2)(:));
     SumFine(i,j,k)  = sum (P1(i1:i2,j1:j2,k1:k2)(:));

     if strcmp(P{}, "PERMX" )
      h_mean          = mean(P1(i1:i2,j1:j2,k1:k2),"h" );	% Harmonic mean for each I-rows
      ha_mean(i,j,k)  = mean(h_mean(:));			% Arithmetic mean for all harmonic k
     
      a_mean          = mean(P1(i1:i2,j1:j2,k1:k2), 3 );	% Arithmetic mean for each K-plane => DIM = 3
      a_mean          = mean(a_mean, 2 );			% Arithmetic mean for each J-plane => DIM = 2
      ah_mean(i,j,k)  = mean(a_mean(:),"h" );			% Harmonic mean for all mean JK-planes     
     end
     
     
    end
   end
  end
  DiffMeanFine = MeanFine .- P2;
  DiffSumFine  = SumFine  .- P2;
  
  MeanName     = ["Mean_Fine_",P{1}];
  DiffMeanName = ["Diff_Mean_Fine_",P{1}];
  SumName      = ["Sum_Fine_",P{1}];
  DiffSumName  = ["Diff_Sum_Fine_",P{1}];
  
  riSetGridProperty(MeanFine,     Case(CaseNo(2)).CaseId, GridNo, MeanName);		# Write mean of Fine model to Coarse model
  riSetGridProperty(DiffMeanFine, Case(CaseNo(2)).CaseId, GridNo, DiffMeanName);	# Write diff of mean of Fine model to Coarse model
  riSetGridProperty(SumFine,      Case(CaseNo(2)).CaseId, GridNo, SumName); 		# Write sum of Fine model to Coarse model
  riSetGridProperty(DiffSumFine,  Case(CaseNo(2)).CaseId, GridNo, DiffSumName);		# Write diff of sum of Fine model to Coarse model

  disp([" Wrote Fine scale data to case:  ",Case(CaseNo(2)).CaseName, ", to the Cell Result ""Generated"" folder."]);
  
  % Cross-plot average Fine Scale data vs Coarse Scale data
  h=figure(numFig);
  hold on
  plot([0 max(P2(:))], [0 max(P2(:))], 'k','LineWidth', 3);
  plot(P2(:),MeanFine(:), "+r; Arithmetic Mean ;");
 
  if strcmp(P{}, "PERMX" )
   avg_ha_ah = ( ha_mean + ah_mean ) / 2;
   plot(P2(:),ha_mean(:),  "xb; Harm-Arith Mean ;");   
   plot(P2(:),ah_mean(:),  "dm; Arith-Harm Mean ;");
   plot(P2(:),avg_ha_ah(:),"sg; Avg HA+AH       ;");
  end
  xlabel({'Coarse Scale Model: ' P{} });
  ylabel({'Upscaled Fine Scale Model: ', P{} });
  title({'Crossplot Upscaled Fine Scale vs Coarse Scale: ' P{} });  
  legend location northwest;
  hold off
  numFig = numFig + 1;

 % Probability-plot Fine Scale data vs Coarse Scale data
 h=figure(numFig);
 hold on
 
 xmax = max(max(P1(:)),max(P2(:)));
 xint = xmax / numBin;
 x    = [0:xint:xmax];
 yP1  = hist(P1(:), x, 1);
 yP2  = hist(P2(:), x,1 );
 yP1m = hist(MeanFine(:), x, 1);
 
 plot(x, yP1,  "-+m; Fine scale ;",     'LineWidth', 3);
 plot(x, yP1m, "-xb; Fine scale Mean ;",'LineWidth', 3);
 plot(x, yP2,  "-k;  Coarse Scale ;",   'LineWidth', 3); 
 
 xlabel({'Parameter ' P{} });
 ylabel('Probability ');
 title({'Probability plot Fine Scale vs Coarse Scale: ' P{} });  
 legend location northwest;
 hold off
 numFig = numFig + 1;
   
 end


#----------------------------------------------------------------------------------------------
 if FineCellDist
  for ijk = Cells'
   % Define Fine scale grid indexes from Coarse scale indexes
   i1 = GridRatio(1).*( ijk(1) - 1) + 1;
   i2 = GridRatio(1).*  ijk(1);
   j1 = GridRatio(2).*( ijk(2) - 1) + 1;
   j2 = GridRatio(2).*  ijk(2);
   k1 = GridRatio(3).*( ijk(3) - 1) + 1;
   k2 = GridRatio(3).*  ijk(3);
   
   MeanFine(ijk(1),ijk(2),ijk(3)) = mean(P1(i1:i2,j1:j2,k1:k2)(:));
   SumFine (ijk(1),ijk(2),ijk(3)) = sum (P1(i1:i2,j1:j2,k1:k2)(:));
   
   if print_hist_to_file
    h=figure(numFig);
    %numFig++;
    hist(P1(:,i),numBin,1)
 %   title(['Statistics for ', P{},', time step ',num2str(i)])
    ylabel('Probability')
    xlabel(P{})
    ax = axis;
    text_xpos = ax(1)+(ax(2)-ax(1))*0.75;
    text_ypos = ax(3)+(ax(4)-ax(3))*0.93;
    L = text(text_xpos, text_ypos, ...
            ["Mean = ", num2str(Mean_arithmetic,   '%5.4f'),...
           "\n",PLowName, "  = ", num2str(Prc_Low, '%5.4f'),...
           "\n",PHighName,"  = ", num2str(Prc_High,'%5.4f')  ]);

    filename=[printFolder,"Histogram_",P{},"_ts_",num2str(i),"_",CurrentCase.CaseName,".png"];
    print(filename,"-dpng");
   end  % if print 
   
  end
 end
    
end
