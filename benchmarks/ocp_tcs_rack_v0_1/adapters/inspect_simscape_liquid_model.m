function report = inspect_simscape_liquid_model(sourceRoot, outputPath)
%INSPECT_SIMSCAPE_LIQUID_MODEL Record a read-only DataCenterCooling inventory.
%   REPORT = INSPECT_SIMSCAPE_LIQUID_MODEL(SOURCEROOT, OUTPUTPATH) opens the
%   MathWorks Data-Center-Simscape project only to inspect the published
%   DataCenterCooling model structure. It does not simulate, save, or alter
%   the external source. The resulting JSON inventory supports adapter-design
%   review; it is not a canonical-case result or a validation record.

arguments
    sourceRoot (1,1) string
    outputPath (1,1) string
end

projectPath = fullfile(sourceRoot, "DataCenterDesignSimscape.prj");
modelPath = fullfile(sourceRoot, "Workflow", "HVAC", ...
    "DatacenterLiquidCooling", "DataCenterCooling.slx");
if ~isfile(projectPath)
    error("ocp_tcs_rack:missingProject", ...
        "Data-Center-Simscape project was not found: %s", projectPath);
end
if ~isfile(modelPath)
    error("ocp_tcs_rack:missingModel", ...
        "DataCenterCooling model was not found: %s", modelPath);
end

openProject(projectPath);
[~, modelName] = fileparts(modelPath);
load_system(modelPath);
cleanup = onCleanup(@() close_system(modelName, 0)); %#ok<NASGU>

allBlocks = find_system(modelName, "LookUnderMasks", "all", ...
    "FollowLinks", "on", "Type", "Block");
blockPaths = string(allBlocks);
relativePaths = extractAfter(blockPaths, strlength(modelName));
keywords = ["cdu", "pipe", "pump", "flow", "temperature", ...
    "sensor", "measure", "server", "rack", "thermal"];
isRelevant = any(contains(lower(relativePaths), keywords), 2);
relevantPaths = blockPaths(isRelevant);

report = struct;
report.report_type = "simscape_liquid_model_inventory";
report.report_schema_version = "0.1";
report.generated_at_utc = char(datetime("now", "TimeZone", "UTC", ...
    "Format", "yyyy-MM-dd'T'HH:mm:ss'Z'"));
report.scope = [ ...
    "Read-only structural inspection. No simulation or model save was " ...
    "performed, and this report is not a benchmark result."
];
report.model = struct( ...
    "source_root", char(sourceRoot), ...
    "project_path", char(projectPath), ...
    "model_path", char(modelPath), ...
    "model_name", modelName, ...
    "stop_time", safe_get_parameter(modelName, "StopTime"), ...
    "solver_name", safe_get_parameter(modelName, "SolverName"), ...
    "all_block_count", numel(allBlocks), ...
    "relevant_block_count", numel(relevantPaths));
report.relevant_blocks = build_block_inventory(relevantPaths);
representativeServerPath = modelName + ...
    "/DataCenter/Datacenter/ServerUnits/Datacenter_1_1";
report.representative_server_unit = ...
    build_representative_server_inventory(representativeServerPath);

outputFolder = fileparts(outputPath);
if strlength(outputFolder) > 0 && ~isfolder(outputFolder)
    mkdir(outputFolder);
end
write_json(outputPath, report);

if nargout == 0
    fprintf("Wrote read-only model inventory: %s\n", outputPath);
end
end

function serverInventory = build_representative_server_inventory(blockPath)
% Record only mask values relevant to the published server load definition.
serverInventory = struct( ...
    "path", char(blockPath), ...
    "available", false, ...
    "mask_values", struct);
if ~ishandle(get_param(blockPath, "Handle"))
    return
end

serverInventory.available = true;
names = string(get_param(blockPath, "MaskNames"));
values = string(get_param(blockPath, "MaskValues"));
selectedNames = [ ...
    "peakPowCPU", "peakPowCPU_unit", "numOfCPU", "numOfCPU_unit", ...
    "peakPowMemory", "peakPowMemory_unit", "numOfMemory", "numOfMemory_unit", ...
    "peakPowDisk", "peakPowDisk_unit", "numOfDisk", "numOfDisk_unit", ...
    "peakPowPCIslot", "peakPowPCIslot_unit", "numOfPCIslot", "numOfPCIslot_unit", ...
    "peakPowMotherboard", "peakPowMotherboard_unit", ...
    "numOfMotherboard", "numOfMotherboard_unit", ...
    "peakPowFan", "peakPowFan_unit", "numOfFan", "numOfFan_unit", ...
    "powerSupplyEff", "powerSupplyEff_unit", "numCPUperServer", ...
    "numCPUperServer_unit", "ratioActualToNameplate", ...
    "ratioActualToNameplate_unit", "idlePower", "idlePower_unit"];

for index = 1:numel(selectedNames)
    parameterName = selectedNames(index);
    parameterIndex = find(names == parameterName, 1);
    if isempty(parameterIndex)
        serverInventory.mask_values.(char(parameterName)) = "";
    else
        serverInventory.mask_values.(char(parameterName)) = ...
            char(values(parameterIndex));
    end
end
end

function blockInventory = build_block_inventory(blockPaths)
blockInventory = repmat(struct( ...
    "path", "", "block_type", "", "reference_block", "", ...
    "mask_type", "", "mask_names", {{}}), numel(blockPaths), 1);

for index = 1:numel(blockPaths)
    blockPath = blockPaths(index);
    blockInventory(index).path = char(blockPath);
    blockInventory(index).block_type = safe_get_parameter(blockPath, "BlockType");
    blockInventory(index).reference_block = safe_get_parameter(blockPath, "ReferenceBlock");
    blockInventory(index).mask_type = safe_get_parameter(blockPath, "MaskType");
    blockInventory(index).mask_names = safe_get_mask_names(blockPath);
end
end

function value = safe_get_parameter(blockPath, parameterName)
try
    value = char(string(get_param(blockPath, parameterName)));
catch
    value = "";
end
end

function names = safe_get_mask_names(blockPath)
try
    names = cellstr(string(get_param(blockPath, "MaskNames")));
catch
    names = {};
end
end

function write_json(outputPath, report)
fileIdentifier = fopen(outputPath, "w");
if fileIdentifier < 0
    error("ocp_tcs_rack:inspectionOutput", ...
        "Could not open inspection output file: %s", outputPath);
end
cleanup = onCleanup(@() fclose(fileIdentifier)); %#ok<NASGU>
fprintf(fileIdentifier, "%s\n", jsonencode(report, PrettyPrint=true));
end
