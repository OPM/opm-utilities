function [mb, cnv, curve_pos, raw] = readInfoIter(fname)
%Import INFOITER Information From OPM Flow Simulation
%
% SYNOPSIS:
%   [mb, cnv, curve_pos, raw] = readInfoIter(fname)
%
% PARAMETERS:
%   fname - Filename.  Assumed to name a .INFOITER file from an OPM Flow
%           simulation run.  This file will be opened using FOPEN mode
%           'rt' and read using function TEXTSCAN.
%
% RETURNS:
%   mb        - Material Balance values.  Collection of all applicable MB_*
%               columns.  Structure with the following fields
%                  * value -- Numerical values
%                  * label -- Cell array of character vectors
%
%   cnv       - Convergence Metric values.  Collection of all applicable
%               CNV_* columns.  Structure with the following fields
%                  * value -- Numerical values
%                  * label -- Cell array of character vectors
%
%   curve_pos - Indirection map into the curve values.  In particular,
%               rows [curve_pos(i) : curve_pos(i + 1) - 1] in 'mb.value'
%               and 'cnv.value' hold the values for curve/convergence
%               history 'i'.
%
%   raw       - Raw data from INFOITER file.  Mostly for debugging
%               purposes.
%
% SEE ALSO:
%   fopen, textscan.

   [fid, msg] = fopen(fname, 'rt');
   if fid < 0
      error('FileOpen:Failure', ...
            'Failed to Open INFOITER File ''%s'': %s', fname, msg);
   end

   c = onCleanup(@() fclose(fid));

   [raw, mb, cnv] = read_raw_data(fid);
   curve_pos = compute_start_positions(raw.Iteration);
end

%--------------------------------------------------------------------------

function [raw, mb, cnv] = read_raw_data(fid)
   header = textscan(fgetl(fid), '%s');
   fmt    = repmat({'%f '}, size(header{1}));

   % Add more string/categorical columns as needed.
   is_categorical = identify_columns(header, { 'WellStatus' });
   fmt(is_categorical) = {'%C '};

   fmt    = [reshape(fmt, 1, []), {'%*[^\n]'}];
   values = textscan(fid, [fmt{:}]);
   raw    = cell2struct(values, header{1}, 2);

   collect_colums0 = @(ix) ...
      struct('value', [ values{ix} ], ...
             'label', { regexprep(header{1}(ix), '_', '.') });

   collect_columns = @(pattern) ...
      collect_colums0(~ cellfun('isempty', regexp(header{1}, pattern)));

   mb  = collect_columns('^MB_');
   cnv = collect_columns('^CNV_');
end

%--------------------------------------------------------------------------

function curve_pos = compute_start_positions(iters)
   curve_pos = find([true; iters(2:end) < iters(1:end-1); true]);
end

%--------------------------------------------------------------------------

function col = identify_columns(header, columns)
   [i, j] = blockDiagIndex(numel(header{1}), numel(columns));
   col = any(reshape(strcmp(header{1}(i), columns(j)), ...
                     numel(header{1}), []), 2);
end
