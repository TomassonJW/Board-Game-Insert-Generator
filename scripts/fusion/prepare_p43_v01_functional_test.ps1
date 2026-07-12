param(
    [string] $RepoRoot,
    [string] $ProjectPath,
    [string] $TargetPath,
    [switch] $DryRun
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_fusion_helpers.ps1"

$root = Resolve-BgigRepoRoot -RepoRoot $RepoRoot
$target = Get-BgigFusionAddinTargetPath -TargetPath $TargetPath
$commit = Get-BgigCurrentCommit -RepoRoot $root
if (-not $ProjectPath) {
    $ProjectPath = Join-Path $root "examples\p43_v01_functional_project.json"
}
$resolvedProject = Resolve-Path -LiteralPath $ProjectPath -ErrorAction Stop
$cadIrPath = Join-Path $env:TEMP ("bgig-p43-v01-functional-{0}.cad-ir.json" -f $commit)

Write-Output "BGIG P43 MVP V0.1 Fusion preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Project: $($resolvedProject.Path)"
Write-Output "Generation mode: compact_only"
Write-Output "CAD IR output: $cadIrPath"

if ($DryRun) {
    Write-Output "Dry run: would export the P43 functional V0.1 CAD IR."
}
else {
    $env:PYTHONPATH = Join-Path $root "src"
    & python -m board_game_insert_generator export-project-v1-cad $resolvedProject.Path --output $cadIrPath
    if ($LASTEXITCODE -ne 0) {
        throw "P43 functional CAD IR export failed."
    }
}

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$settings = @{
    action = "generate"
    input_mode = "cad_ir_file"
    generation_mode = "compact_only"
    cad_ir_path = $cadIrPath
    config_json_path = ""
    project_root = $root
}
Write-BgigFusionUiSettings -TargetPath $target -Settings $settings -DryRun:$DryRun

Write-Output ""
Write-Output "Fusion actions remaining:"
Write-Output "1. Open Fusion 360 and an Assembly-compatible design."
Write-Output "2. Run BoardGameInsertGenerator from Utilities > Add-ins."
Write-Output "3. Click Run once."
Write-Output "4. Check the compact scene: 3 named storage trays, one empty tray, one separator, their top-open cavities, and one reference-box outline."
Write-Output "5. Confirm there is no error and no duplicate BGIG scene."
Write-Output "Prepared P43 MVP V0.1 Fusion smoke test: $(-not $DryRun)"
