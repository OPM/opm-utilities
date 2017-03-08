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

% User's choice  ---------------------------------------------------------------------------------------------

P_dynamic = {"PRESSURE" "SOIL"};   % If print_all_dynamic = false, select parameters manually, e.g.: "PRESSURE"
print_all_dynamic  = false;        % Set 'true' or  'false' if all dynamic parameter should be printed or not
print_plot_to_file = true;
print_data_to_file = true;
printFolder = '/private/hhgs/ri/';

Cell(1,1:3) = [70 45 16];   % I J K for cells to be plotted
Cell(2,1:3) = [70 45 17];

%-------------------------------------------------------------------------------------------------------------

GridNo=0;					# Main grid number = 0
DIM = riGetGridDimensions();
Days = riGetTimeStepDays();
Dates = riGetTimeStepDates();
CurrentCase = riGetCurrentCase();
Time=[[Dates.Year]' [Dates.Month]' [Dates.Day]' [Dates.Hour]' [Dates.Minute]' [Dates.Second]'];


% Find all dynamic properties in case
if (print_all_dynamic == true)
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


% Plot cell value vs time
numFig = 1;
lgd = [];
data = [Days];

for P = P_dynamic
 P1  = riGetGridProperty(GridNo,P{1});	# Load parameter
 [nx ny nx tsteps] = size(P1);

  colorhsv=hsv(rows(Cell));
  set (0, 'defaulttextfontname', 'Courier');

  h=figure(numFig);
  hold on
  for i=1:rows(Cell)
   plot (Days, P1(Cell(i,1),Cell(i,2),Cell(i,3),:),'color',colorhsv(i,:),'LineWidth',1.5); 
   txt = ["Cell(", num2str(Cell(i,1))," " num2str(Cell(i,2)), " ",num2str(Cell(i,3)),") "];
   data(:,i+1) = P1(Cell(i,1),Cell(i,2),Cell(i,3),:);

   if i==1
     lgd = [cellstr(txt)];
   else
     lgd = [lgd cellstr(txt)];
   end
  end  % endfor cell rows to plot

  xlabel('Time (Days)');   %'FontName', 'Arial'
  ylabel( P{} );
  legend( lgd{} );
  legend location northeastoutside;
  title({'Cell values vs Time ', P{}} );

  if print_data_to_file
   filename=[printFolder,"Plot_Cell_",P{},"_",CurrentCase.CaseName,".png"];

   print(filename,"-dpng");

   % print values to acsii-file
   formatSpec=["%12.3f "];
   for i=1:rows(Cell)
    formatSpec = [formatSpec "%10.3f "];
    idx = [    " (", num2str(Cell(i,1))," " num2str(Cell(i,2)), " ",num2str(Cell(i,3)),") "];  % header cell indexes
    if i==1
     ijk = [cellstr(idx)];
    else
     ijk = [ijk cellstr(idx)];
    end %if else
   end % for cell rows
   formatSpec = [formatSpec ' \n'];

   outfilename=[printFolder,"Print_Cell_",P{},"_",CurrentCase.CaseName,".txt"];
   fid = fopen(outfilename,'w');
   fprintf(fid, '%s %s \n', P{}, CurrentCase.CaseName);   % Header - parameter and case name
   fprintf(fid, '%s %s \n', "       Time  ", [ijk{}]'');  % Header - table
   fprintf(fid, formatSpec, data'(:) );
   fclose(fid);  end  % endif print to file

  numFig=numFig+1; 
end
