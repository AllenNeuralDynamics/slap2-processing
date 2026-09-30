function slap2_run_motion_correction(jobFile)
% SLAP2_RUN_MOTION_CORRECTION Run the GIAnT-MATLAB motion correction for one job file.
%   Reads the JSON job written by slap2_processing_library.matlab.bridge.write_job, calls
%   GIAnT-MATLAB, and writes the result JSON listing the outputs. Not implemented yet.
job = jsondecode(fileread(jobFile)); %#ok<NASGU>
error('slap2:notImplemented', 'slap2_run_motion_correction is a stub; see docs/design/matlab-transition.md');
end
