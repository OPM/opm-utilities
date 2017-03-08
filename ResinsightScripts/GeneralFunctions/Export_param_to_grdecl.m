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
print_to_sceen  = true;
print_to_file	= true;
printFolder = '/project/multiscale/OPM/Ceetron/simu/ERTcase/';  % Note! End with "/"
printOutputFileName = 'test_x_y_z_v1_export.txt'

#----------------------------------------------------------------------------------------
# Retrive data from ResInsight
#
CurrentCase = riGetCurrentCase();
CInfo  = riGetActiveCellInfo();
Center = riGetActiveCellCenters();
DIM    = riGetGridDimensions();
PARAM  = riGetActiveCellProperty( PROP );

# Shift negative z-depth to positive values
Center(:,3) = - Center(:,3); 
[N,TS] = size(PARAM);

# Select one timestep if multiple
if (TS > 1) 
 PARAM1 = PARAM(:,TimeStep);
end

minI = min( CInfo(:,2) );
maxI = max( CInfo(:,2) );
minJ = min( CInfo(:,3) );
maxJ = max( CInfo(:,3) );

topK_active  = zeros(DIM(1), DIM(2));
topK_rowIDX  = topK_active; 

for i = minI : maxI
 for j = minJ : maxJ
   
   row = [];
   
   row = find( (CInfo(:,2) == i) & (CInfo(:,3) == j) );
   
     
   if (isempty(row) == 0) 
    if (row(1) > 0)
     
     topK_rowIDX(i,j) = row(1);
     topK_active(i,j) = CInfo(row(1), 4);
     
    end
   end
 
 end
end

if print_to_sceen
# Print header
 printf("\n%s %s   \n", ("# Upper active cell value for simulation run:  "), CurrentCase.CaseName ); 
 printf("# Property:  %s,  Timestep %i \n", PROP, TimeStep)
 printf("# Cell Center UTM and Cell Value \n")
 printf("#%11s %11s  %11s %11s %5s  %5s %5s \n", ("UTM E"),("UTM N"),("TVD"), PROP,("I"),("J"),("K") )
 printf("%s  \n",("#---------------------------------------------------------------------------------------------"));
 

for i = minI : maxI
 for j = minJ : maxJ
     
   if ( topK_rowIDX(i,j) > 0 )
    
    printf(" %11.2f %11.2f %11.2f %11.2f  %5i  %5i %5i \n", Center(topK_rowIDX(i,j),:), PARAM1(topK_rowIDX(i,j)), i, j, topK_active(i,j) )
   
   end 
 
 end
end
end %print to screen


if print_to_file
  
 outfilename=[printFolder, printOutputFileName];
 
 fid = fopen(outfilename,'w'); 
 
 fprintf(fid,"%s %s   \n", ("# Export of upper active cell value for simulation run:  "), CurrentCase.CaseName ); 
 fprintf(fid,"# Property:  %s,  Timestep %i \n", PROP, TimeStep)
 fprintf(fid,"# Cell Center UTM and Cell Value \n")
 fprintf(fid,"#%11s %11s  %11s %11s %5s  %5s %5s \n", ("UTM E"),("UTM N"),("TVD"), PROP,("I"),("J"),("K") )
 fprintf(fid,"%s  \n",("#---------------------------------------------------------------------------------------------"));

for i = minI : maxI
 for j = minJ : maxJ
     
   if ( topK_rowIDX(i,j) > 0 )
    
    fprintf(fid," %11.2f %11.2f %11.2f %11.2f  %5i  %5i %5i \n", Center(topK_rowIDX(i,j),:), PARAM1(topK_rowIDX(i,j)), i, j, topK_active(i,j) )
   
   end 
 
 end
end

 fclose(fid);  
end  %print_COMPDAT_to_file



   
   
