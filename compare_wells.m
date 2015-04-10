%% check/load OPM and eclipse-results
mrstModule add ad-fi deckformat

fn = 'NORNE_ATW2013';
outputdir_ecl = '../opm-data/norne/';
outputdir_opm = '../opm-data/norne/output_ntg/';
%% Grid
if(0)
deck = readEclipseDeck([fn,'.DATA']);
% The deck is given in field units, MRST uses metric.
deck = convertDeckUnits(deck);
G = initEclipseGrid(deck);
G = computeGeometry(G);
end


%% Welldata
smry_opm = readSummaryLocal([outputdir_opm,fn]);
smry_ecl = readSummaryLocal([outputdir_ecl,fn]);

ind_ecl = 1:size(smry_ecl.data,2);
ind_opm = 1:size(smry_opm.data,2);

time_opm =  smry_opm.get(':+:+:+:+', 'TIME', ind_opm);
time_ecl =  smry_ecl.get(':+:+:+:+', 'TIME', ind_ecl);

%% Plot Producer WOPR
%wellnames = {'D-1H','B-2H','C-4H'};
wellnames_ecl = {smry_ecl.WGNAMES{2:end}};
wellnames_opm = {smry_opm.WGNAMES{2:end}};
wellnames = intersect(wellnames_ecl,wellnames_opm);

keywords = {'WBHP','WGIR','WWIR','WOPR','WGPR','WWPR'};
ylabels = {'barsa','m^3/day','m^3/day','m^3/day','m^3/day','m^3/day','m^3/day'};
save = false;
h = figure;
set(h,'PaperPosition',[0.634517 6.34517 30.3046 15.2284])
for i = 1:numel(wellnames)
    
    wellname = wellnames{i};
    
    for j = 1 : numel(keywords)
        keyword = keywords{j};
        
        opm = smry_opm.get(wellname, keyword, ind_opm)';
        ecl = smry_ecl.get(wellname, keyword, ind_ecl)';

        if ~isempty(ecl) 
            clf
            axes('FontSize',20);
            hold on
            plot(time_opm, opm, '-+r','MarkerSize',5,'Linewidth',2);
            plot(time_ecl, ecl, '-ob','MarkerSize',5,'Linewidth',2);
            legend({'OPM', 'Eclipse'},'Location','NorthEastOutside')
            xlabel('Days')
            ylabel(ylabels{j});
            title([wellname,':',keyword])
            pause
            if save
                saveas(gcf, [outputdir,'/norne_',wellname,'_',keyword], 'jpg')
            end
        end
       

    end
end
