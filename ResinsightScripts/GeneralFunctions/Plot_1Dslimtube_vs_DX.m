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

clear;clc;close all;
% User choice:
print_all_dynamic = true;     % Set 'true' or  'false' if all dynamic parameter should be printed or not
P_dynamic = {"SGAS" "SOIL"};   % For selecting parameters manually, e.g.: "PRESSURE" "MLSC1"
%------------------------------
GridNo=0;					# Main grid number = 0
DX  = riGetGridProperty(GridNo,"DX");
DIM = riGetGridDimensions();
Days = riGetTimeStepDays();
Dates = riGetTimeStepDates();
CurrentCase = riGetCurrentCase();
Time=[[Dates.Year]' [Dates.Month]' [Dates.Day]' [Dates.Hour]' [Dates.Minute]' [Dates.Second]'];

if (print_all_dynamic == true)
 % Find all dynamic properties in case
 Prop = riGetPropertyNames();
 numProp = rows(Prop);
 numDynamic = 1;
 for i=1:numProp
   if strcmp(Prop(i).PropType,"DynamicNative");
     P_dynamic(numDynamic) = {Prop(i).PropName};
     numDynamic++;
   endif
 endfor
 disp("Found dynamic parameters:")
end

% Calculate sum DX along model
DX(1)=0; % Dummy cell for injector well
DX(end)=0; % Dummy cell for producer well
SumDX = DX;
for i=2:DIM(1)
 SumDX(i)=SumDX(i-1)+DX(i-1)/2+DX(i)/2; % x-distance as mid point in cells
end

% Plot along x-axis for all time steps for all dynamic parameters
numFig=1;
lgd=[];

for P = P_dynamic
 P1  = riGetGridProperty(GridNo,P{1});	# Load parameter
 [nx ny nx tsteps] = size(P1);
 
  colorhsv=hsv(tsteps+2);
  set (0, 'defaulttextfontname', 'Courier');

  h=figure(numFig);
  hold on
  for ts=1:tsteps
   plot(SumDX, P1(:,1,1,ts),'color',colorhsv(ts,:),'LineWidth',1.5);
   Days_correct=round(Days*1000)/1000+0.125;                  % correction due to bug in riGetTimeStepDays()
   txt=["Time ", num2str(Days_correct(ts), "%4.3f")," day(s)"];
   if ts==1
     lgd=[cellstr(txt)];
    else
     lgd=[lgd cellstr(txt)];
    end
  end 
  xlabel('Distance in x-direction');   %'FontName', 'Arial'
  ylabel( P{} );
  legend( lgd{} );
  legend location northeastoutside;
  title({'Slim Tube simulation ', P{}} );
  xlim([SumDX(1) SumDX(end)])
  %print plot to file
  folder='/project/temp/hhgs/SlimTube/';
  filename=[folder,"Plot_",P{},"_",CurrentCase.CaseName,".png"];
  print(filename,"-dpng");
  %print data to file
  outfilename=[folder,"Print_",P{},"_",CurrentCase.CaseName,".txt"];
  fid = fopen(outfilename,'w');              % Output filename
  formatSpec=[];
  for ts=1:tsteps
   formatSpec = [formatSpec "%8f "];
  end
  formatSpec = [formatSpec ' \n'];
  fprintf(fid, '%s %s \n', P{}, CurrentCase.CaseName);   % Heading - parameter and case name
  fprintf(fid, '%s  \n', "Rows = cell values in x-direction. Colums = Time steps");
  P1_2d = reshape(P1, DIM(1), tsteps);                         % Remove y and z dimensions
  fprintf(fid, formatSpec, P1_2d'(:) );
  fclose(fid);
  numFig=numFig+1; 
end
