function visualiseOpmNonlinConv(curvePos, errors, labels, metrics, varargin)
%Visualise Error Metrics and Iteration Flags From OPM's INFOITER Data
%
% SYNOPSIS:
%   visualiseOpmNonlinConv(curvePos, errors, labels, metrics)
%   visualiseOpmNonlinConv(curvePos, errors, labels, metrics, 'pn1', pv1, ...)
%
% PARAMETERS:
%   curvePos - Indirection map 'curve_pos' from readInfoIter.
%
%   errors   - Error measures from analyseOpmNonlinConv.
%
%   labels   - Convergence metric axis labels from analyseNonlinConv.
%
%   metrics  - Inferred convergence indicators from analyseNonlinConv.
%
%   'pn'/pv  - Optional parameters passed as 'key'/value pairs.  Supported
%              options are:
%                * steps  -- Ministeps for which to generate visual output.
%                            Subset of 1:NUMEL(curvePos)-1.  Default value:
%                            metrics.flaggedSteps.
%
%                            The visualisation function will stop with an
%                            error diagnostic if this set (array) of steps
%                            is empty.
%
%                * figure -- Figure window into which generate visual
%                            output.  If a figure window with this ID does
%                            not exist, a new figure window with this ID
%                            will be created.  Default value: figure=[]
%                            (empty) which creates a new figure window
%                            whose ID is determined by MATLAB.
%
%                            If 'figure' is not a nominally valid figure
%                            ID--i.e., if 'figure' is not a positive
%                            integer--then the ID request is ignored and
%                            this function will behave as if the caller did
%                            not specify the 'figure' option.
%
% SEE ALSO:
%   readInfoIter, analyseOpmNonLinConv.

   opt = struct('steps', metrics.flaggedSteps, ...
                'figure', []);
   opt = merge_options(opt, varargin{:});

   if isempty(opt.steps)
      error('StepList:Empty', 'Step list must not be empty');
   end

   dash = create_dashboard(opt);

   for step = reshape(opt.steps, 1, [])
      draw_step(dash, step, curvePos, errors, labels, metrics);
   end
end

%--------------------------------------------------------------------------

function dash = create_dashboard(opt)
   dash.fig = get_figure(opt.figure);

   if ~isa(dash.fig, 'Figure')
      dash.fig = figure(dash.fig);
   end

   set(0, 'CurrentFigure', dash.fig);
   clf(dash.fig, 'reset');

   [width, height] = deal(0.34, 0.40);
   x = [0.13, 0.57];
   y = [0.06, 0.52];

   dash.ax.flag = axes(dash.fig, 'Position', [x(1), y(2), width, height]);
   dash.ax.dist = axes(dash.fig, 'Position', [x(1), y(1), width, height]);
   dash.ax.conv = axes(dash.fig, 'Position', [x(2), y(1), width, height]);
end

%--------------------------------------------------------------------------

function draw_step(dash, step, curvePos, errors, labels, metrics)
   rowIx = reshape(curvePos(step) : curvePos(step + 1) - 1, [], 1);
   success = metrics.conv(step);

   draw_flags(dash, success, rowIx, metrics);
   draw_distance(dash, success, rowIx, metrics);
   draw_convergence(dash, rowIx, errors, labels);
end

%--------------------------------------------------------------------------

function draw_flags(dash, success, rowIx, metrics)
   cla(dash.ax.flag, 'reset')
   set(dash.ax.flag, 'NextPlot', 'add')  % hold on

   bar(dash.ax.flag, metrics.flag(rowIx, :), 'stacked');
   plot(dash.ax.flag, 0.5 + [0, numel(rowIx)], ...
        [metrics.maxFail, metrics.maxFail], ...
        '--k', 'LineWidth', 1)

   legend(dash.ax.flag, 'Fail', 'Dist', 'Stop', ...
          'Location', 'northwest');

   ylim = get(dash.ax.flag, 'YLim');
   set(dash.ax.flag, ...
       { 'YLim', 'Color' }, ...
       { [ylim(1), max(ylim(2), 15)], ...
         background_colour(success) })
end

%--------------------------------------------------------------------------

function draw_distance(dash, success, rowIx, metrics)
   cla(dash.ax.dist, 'reset')
   set(dash.ax.dist, 'NextPlot', 'add')  % hold on

   yyaxis(dash.ax.dist, 'left')
   bar(dash.ax.dist, metrics.fail(rowIx), ...
       'FaceColor', [0.6, 0.6, 1]);

   yyaxis(dash.ax.dist, 'right')
   plot(dash.ax.dist, metrics.dist(rowIx), '-o', ...
        'MarkerSize', 4, 'MarkerFaceColor', 'r', ...
        'LineWidth', 1);

   set(dash.ax.dist, 'Color', background_colour(success))
end

%--------------------------------------------------------------------------

function draw_convergence(dash, rowIx, errors, labels)
   cla(dash.ax.conv, 'reset')

   [m, n] = deal(size(errors, 2), numel(rowIx));

   errMax = max([max(max(errors(rowIx,:))), 6]);
   axLim  = [zeros([1, m]); repmat(errMax, [1, m])];

   spider_plot(errors(rowIx, :),                ...
               'AxesHandle',      dash.ax.conv, ...
               'AxesLimits',      axLim,        ...
               'AxesLabels',      labels,       ...
               'AxesDisplay',     'none',       ...
               'AxesInterpreter', 'none',       ...
               'AxesWebType',     'circular',   ...
               'LabelFontSize',   6,            ...
               'FillOption',      'on',         ...
               'Color',           parula(n));
   zoom(1.2)

   legend(dash.ax.conv, num2str((1 : n) .'), ...
          'NumColumns', 1, 'Location', 'EastOutside')
end

%--------------------------------------------------------------------------

function bgc = background_colour(success)
   bgc = [0.9, 1, 0.9];
   if ~success
      bgc = [1, 0.9, 0.9];
   end
end

%--------------------------------------------------------------------------

function fig = get_figure(fig)
   if (numel(fig) == 1) && (is_figure(fig) || is_valid_figure_number(fig))
      % 'fig' is a single existing Figure object or a single nominally
      % valid figure ID which may or may not identify an existing figure.
      % Activate the existing Figure object or create a figure window (or
      % figure object) with an ID of 'fig'.

      fig = figure(fig);
   else
      % 'fig' is not an existing Figure object or a valid figure ID.
      % Ignore request and create a new figure window/object instead.

      fig = figure();
   end
end

%--------------------------------------------------------------------------

function tf = is_figure(fig)
   if exist('isgraphics', 'builtin')
      tf = isgraphics(fig, 'figure');
   else
      tf = ishghandle(fig) && ismember(fig, findobj('type', 'figure'));
   end
end

%--------------------------------------------------------------------------

function tf = is_valid_figure_number(fig)
   % Valid figure numbers are positive integers
   tf = isnumeric(fig) && (fig > 0) && (mod(fig, 1) == 0);
end
