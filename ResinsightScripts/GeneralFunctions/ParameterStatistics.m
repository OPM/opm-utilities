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
#-----------------------------------------------------------------------------------

clear;clc;close all;

% User's choice  ---------------------------------------------------------------------------------------------
P_list = {"SOIL" "SWAT" "SWCR" "PORO"};   %  Parameters to run statistics
PLow  = 90; 				  % Low Percentile (in %)
PHigh = 10; 				  % High Percentile (in %)
print_plot_to_file = true;
numBin = 50;  			    % If printing to file - set no. of bins for histrogram plot
printFolder = '/private/hhgs/ri/';  % If printing to file - set path
%-------------------------------------------------------------------------------------------------------------
CurrentCase = riGetCurrentCase();
PORV = riGetActiveCellProperty("PORV");   % Weight factor
SWAT = riGetActiveCellProperty("SWAT");   % Weight factor
PLowName  = ["P",num2str(PLow)];
PHighName = ["P",num2str(PHigh)];
numFig = 1;
lgd = [];

for P = P_list 
 P1  = riGetActiveCellProperty(P{1});	% Load parameter
 ts = columns(P1);		% Number of time steps
 PV = [];
 PV   = repmat(PORV, [1 ts]);   % PORV weight function
 HCPV = [];
 HCPV = (1 - SWAT(:,1)).*PORV;	% Only use initial HCPV for weight function
 HCPV = repmat(HCPV, [1 ts]);
 disp("--------------------------------------------------------------------")
 disp(["Parameter: ", P{}])

 if ts > 1
  disp("Statistics over all timesteps")
  Mean_PVweighted   = sum(P1(:) .*   PV(:))/sum(PV(:))
  Mean_HCPVweighted = sum(P1(:) .* HCPV(:))/sum(HCPV(:))
  Mean_arithmetic = mean(P1(:))
  Median = median(P1(:))
  Std = std(P1(:))
  Min = min(P1(:))
  Max = max(P1(:))
  P_Low  = prctile(P1(:),100 - PLow)
  P_High = prctile(P1(:),100 - PHigh)
  disp("--------------------------------------------------------------------")
 end % stat for all ts

  disp("Statistics for each timesteps")
  for i = 1:ts
   disp(["Time step #", num2str(i)," of ",P{}])
   Mean_PVweighted   = sum(P1(:,i) .*  PV(:,i))/sum(PV(:,i))
   Mean_HCPVweighted = sum(P1(:,i) .* HCPV(:,i))/sum(HCPV(:,i))
   Mean_arithmetic = mean(P1(:,i))
   Median = median(P1(:,i))
   Std = std(P1(:,i))
   Min = min(P1(:,i))
   Max = max(P1(:,i))
   Prc_Low  = prctile(P1(:,i),100 - PLow)
   Prc_High = prctile(P1(:,i),100 - PHigh)
   disp("--------------------------------------------------------------------")

   if print_plot_to_file
    h=figure(numFig);
    %numFig++;
    hist(P1(:,i),numBin,1)
    title(['Statistics for ', P{},', time step ',num2str(i)])
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
  end % for each ts
end % for Parameter list


if print_plot_to_file
  disp(["Plots are printed to folder ",printFolder])
  disp(" ")
end

