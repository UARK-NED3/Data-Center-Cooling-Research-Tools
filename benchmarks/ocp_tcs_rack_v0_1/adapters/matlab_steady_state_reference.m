function report = matlab_steady_state_reference(casePath, outputPath)
%MATLAB_STEADY_STATE_REFERENCE Evaluate the v0.1 liquid-side energy balance.
%   This independently implemented MATLAB calculation evaluates the same
%   declared steady balance as the Python oracle. It has no component thermal
%   resistance, hydraulic, CDU, pump, or facility model, and must not be
%   interpreted as a calibrated rack prediction or a Simscape execution.

arguments
    casePath (1,1) string
    outputPath (1,1) string
end

caseData = jsondecode(fileread(casePath));
liquidFraction = caseData.rack.liquid_capture_fraction;
airFraction = caseData.rack.residual_air_heat_fraction;
itHeatW = caseData.rack.it_heat_w;
massFlowKgS = caseData.tcs.mass_flow_kg_s;
specificHeatJKgK = caseData.fluid.specific_heat_j_kg_k;
if abs(liquidFraction + airFraction - 1.0) > 1e-12
    error("ocp_tcs_rack:invalidHeatSplit", ...
        "Liquid and residual-air heat fractions must sum to one.");
end
if itHeatW < 0.0 || massFlowKgS <= 0.0 || specificHeatJKgK <= 0.0
    error("ocp_tcs_rack:nonphysicalInput", ...
        "IT heat must be nonnegative; mass flow and specific heat must be positive.");
end

liquidHeatW = itHeatW * liquidFraction;
airHeatW = itHeatW - liquidHeatW;
temperatureRiseK = liquidHeatW / (massFlowKgS * specificHeatJKgK);
returnTemperatureC = caseData.tcs.supply_temperature_c + temperatureRiseK;

report = struct;
report.adapter_id = "matlab-steady-state-reference-v0.1";
report.case_id = caseData.case_id;
report.evidence_class = "synthetic_derived";
report.matlab_release = char(version("-release"));
report.method = strjoin([ ...
    "Direct steady energy balance; independently implemented in MATLAB. " ...
    "No component, hydraulic, or facility physics is included."
], "");
report.result = struct( ...
    "it_heat_w", itHeatW, ...
    "liquid_heat_w", liquidHeatW, ...
    "air_heat_w", airHeatW, ...
    "tcs_temperature_rise_k", temperatureRiseK, ...
    "tcs_supply_temperature_c", caseData.tcs.supply_temperature_c, ...
    "tcs_return_temperature_c", returnTemperatureC, ...
    "rack_energy_residual_w", itHeatW - liquidHeatW - airHeatW);
report.use_limit = strjoin([ ...
    "Synthetic verification output only; not a calibrated or experimentally " ...
    "validated rack result."
], "");

outputFolder = fileparts(outputPath);
if strlength(outputFolder) > 0 && ~isfolder(outputFolder)
    mkdir(outputFolder);
end
fileIdentifier = fopen(outputPath, "w");
if fileIdentifier < 0
    error("ocp_tcs_rack:output", "Could not open output file: %s", outputPath);
end
cleanup = onCleanup(@() fclose(fileIdentifier)); %#ok<NASGU>
fprintf(fileIdentifier, "%s\n", jsonencode(report, PrettyPrint=true));

if nargout == 0
    fprintf("Wrote MATLAB steady-state reference: %s\n", outputPath);
end
end
