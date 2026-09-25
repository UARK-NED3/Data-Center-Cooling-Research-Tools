function report = matlab_preflight(outputPath)
%MATLAB_PREFLIGHT Check the documented MATLAB environment for the adapter.
%   This function checks only the local MATLAB release and installed products.
%   It does not open, modify, or simulate any third-party Simulink model.

arguments
    outputPath (1,1) string = "matlab_preflight_report.json"
end

requiredProducts = [
    "MATLAB"
    "Simulink"
    "Simscape"
    "Simscape Electrical"
    "Simscape Fluids"
    "Stateflow"
];

installedProductInfo = ver;
installedProducts = string({installedProductInfo.Name})';
missingProducts = setdiff(requiredProducts, installedProducts, "stable");
release = string(version("-release"));
supportedRelease = any(release == ["R2025b", "2025b"]);

report = struct;
report.report_type = "matlab_adapter_preflight";
report.report_schema_version = "0.1";
report.generated_at_utc = char(datetime("now", "TimeZone", "UTC", ...
    "Format", "yyyy-MM-dd'T'HH:mm:ss'Z'"));
report.matlab_release = char(release);
report.required_release = "R2025b";
report.release_supported = supportedRelease;
report.required_products = cellstr(requiredProducts);
report.installed_products = cellstr(installedProducts);
report.missing_products = cellstr(missingProducts);
report.ready = supportedRelease && isempty(missingProducts);
report.scope = [ ...
    "Environment inspection only; no third-party project was opened, " ...
    "changed, or simulated."
];

encodedReport = jsonencode(report, PrettyPrint=true);
fileIdentifier = fopen(outputPath, "w");
if fileIdentifier < 0
    error("ocp_tcs_rack:preflightOutput", ...
        "Could not open preflight output file: %s", outputPath);
end
cleanup = onCleanup(@() fclose(fileIdentifier)); %#ok<NASGU>
fprintf(fileIdentifier, "%s\n", encodedReport);

if nargout == 0
    fprintf("%s\n", encodedReport);
end

if ~report.ready
    error("ocp_tcs_rack:unsupportedEnvironment", ...
        "The documented R2025b adapter environment is not available. See %s.", ...
        outputPath);
end
end
