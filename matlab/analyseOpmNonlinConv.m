function [errors, labels, metrics] = ...
      analyseOpmNonlinConv(mb, cnv, curvePos, raw, varargin)
%Calculate Error Metrics and Iteration Flags From OPM's INFOITER Data
%
% SYNOPSIS:
%   [errors, labels, metrics] = ...
%       analyseOpmNonLinConv(mb, cnv, curvePos, raw)
%
%   [errors, labels, metrics] = ...
%       analyseOpmNonLinConv(mb, cnv, curvePos, raw, 'pn1', pv1, ...)
%
% PARAMETERS:
%   mb       - Material balance structure from readInfoIter.
%
%   cnv      - Convergence metric structure from readInfoIter.
%
%   curvePos - Indirection map 'curve_pos' from readInfoIter.
%
%   raw      - Raw INFOITER data from readInfoIter.
%
%   'pn'/pv  - Optional parameters passed as 'key'/value pairs.  Supported
%              options are:
%                * tol -- Convergence tolerances.  Scalar structure with
%                         known fields 'mb' and 'cnv' defining convergence
%                         thresholds for the material balance and CNV
%                         metrics, respectively.  Default thresholds are
%                         the OPM defaults of mb = 1.0e-6 and cnv = 1.0e-3.
%                         If you omit one of the fields then the internal
%                         default threshold value will be used in its place.
%
%                * maxFail -- Upper bound on number of failures to accept a
%                         given timestep.  Default value: maxFail = 5.
%
%                * distDecrFactor -- Target factor by which the distance to
%                         the convergence box is expected to decrease from
%                         one non-linear iteration to the next in order to
%                         be considered acceptable.
%
%                * inferFailure -- Callback function by which to identify
%                         number of convergence failures within each
%                         non-linear iteration.  Must be a reduction
%                         function which converts an m-by-k array of DOUBLE
%                         to an m-by-1 array of integers. Default value:
%                         @(e) sum(e > 0, 2).
%
%                * calcDistance -- Callback function by which to compute
%                         the distance to the convergence box within each
%                         non-linear iteration.  Must be a reduction
%                         function which converts an m-by-k array of DOUBLE
%                         to an m-by-1 array of DOUBLE.  Default value:
%                         @(e) sum(e, 2).
%
% RETURNS:
%   errors  - Error measures.  An m-by-k array of non-negative DOUBLE
%             values, with 'm' being the total number of non-linear
%             iterations in the run (curvePos(end) - 1), and 'k' being the
%             total number of material balance and CNV metrics.  Individual
%             elements are zero if the corresponding metric is within the
%             convergence box.
%
%   labels  - Convergence metric axis labels.  A 1-by-k cell array of
%             character vectors created by concatenating the input labels
%             for the 'mb' and 'cnv' measures.
%
%   metrics - Inferred convergence indicators for the non-linear solution
%             process.  Scalar structure with the following fields:
%               * fail -- Failure counts.  An m-by-1 array of non-negative
%                         integers.
%
%               * dist -- Convergence box distances.  An m-by-1 array of
%                         non-negative DOUBLE values.
%
%               * conv -- Status flags for step convergence.  An nstep-by-1
%                         LOGICAL array which is TRUE for converged steps
%                         and FALSE otherwise.  The number of steps is
%                         NUMEL(curvePos) - 1.
%
%               * flag -- Failure flags.  An m-by-2 array of non-negative
%                         integers.  Flag(:,1) identifies component
%                         convergence failures and increases by one if the
%                         number of failed components increases from one
%                         non-linear iteration to the next.  Flag(:,2)
%                         identifies convergence rate failures and
%                         increases by one if the convergence box distance
%                         does not decrease at a sufficient rate from one
%                         non-linear iteration to the next.
%
%                         Both flags are reset to zero at the start of the
%                         next timestep (ministep).
%
%               * flaggedSteps -- Index of potentially interesting
%                         timesteps (ministeps).  These are the timesteps
%                         for which the total number of flags, summed over
%                         all flag categories, exceed the accepted upper
%                         bound ('maxFail' option value).
%
%               * maxFail -- Copy of 'maxFail' option value.  Typically for
%                         use by post-processors/visualisers.
%
% SEE ALSO:
%   readInfoIter, visualiseOpmNonlinConv.

   opt = struct('tol'           , default_tolerances(), ...
                'maxFail'       , 5, ...
                'distDecrFactor', 0.75, ...
                'inferFailure'  , @(e) sum(e > 0, 2), ...
                'calcDistance'  , @(e) sum(e, 2));
   opt = merge_options(opt, varargin{:});

   [errors, labels] = compute_errors(mb, cnv, opt);
   [fail, dist, flag] = analyse_errors(errors, opt, curvePos);

   flaggedSteps = ...
      find(sum(flag(curvePos(2:end) - 1, :), 2) > opt.maxFail);

   metrics = struct('fail', fail, 'dist', dist, ...
                    'flag', flag, 'maxFail', opt.maxFail, ...
                    'flaggedSteps', flaggedSteps, ...
                    'conv', identify_successful_steps(curvePos, raw));
end

%--------------------------------------------------------------------------

function tol = default_tolerances()
   tol = struct('mb', 1.0e-6, 'cnv', 1.0e-2);
end

%--------------------------------------------------------------------------

function [error, labels] = compute_errors(mb, cnv, opt)
   tol = merge_structures(default_tolerances(), opt.tol);

   t = rldecode([tol.cnv, tol.mb], [numel(cnv.label), numel(mb.label)], 2);
   error = max(log10(bsxfun(@rdivide, [cnv.value, mb.value], t)), 0);

   labels = [ reshape(cnv.label, 1, []), reshape(mb.label, 1, []) ];
end

%--------------------------------------------------------------------------

function [fail, dist, flag] = analyse_errors(e, opt, curvePos)
   fail = opt.inferFailure(e);
   dist = opt.calcDistance(e);

   iterIx = mcolon(curvePos(1 : end - 1) + 1, curvePos(2 : end) - 1);

   flag = zeros([numel(fail), 2]);
   flag(iterIx, :) = ...
      double([fail(iterIx) >                    fail(iterIx - 1), ...
      dist(iterIx) > opt.distDecrFactor*dist(iterIx - 1)]);

   flag = cumsum(flag, 1);
   flag = flag - rldecode(flag(curvePos(1:end-1), :), diff(curvePos));
end

%--------------------------------------------------------------------------

function success = identify_successful_steps(curvePos, raw)
   step = [raw.ReportStep, raw.TimeStep];
   last = curvePos(2 : end - 1) - 1;  % Last iteration of previous step
   frst = last + 1;                   % First iteration of current step

   % Step succeeded if we advanced to next
   %   1. Report step (step(:,1))
   %   2. Time step within current report step (step(:,2), "ministep")
   success = [any(step(frst,:) > step(last,:), 2); true];
end

%--------------------------------------------------------------------------

function s = merge_structures(s, s2)
   vargs = reshape([reshape(fieldnames (s2), 1, []); ...
                    reshape(struct2cell(s2), 1, [])], 1, []);

   [s, extra] = merge_options(s, vargs{:});

   for kv = reshape(extra, 2, [])
      s.(kv{1}) = kv{2};
   end
end
