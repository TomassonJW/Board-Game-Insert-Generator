param(
    [string] $RepoRoot,
    [ValidateSet("mixed-box", "card-game", "board-game")]
    [string] $StarterId = "mixed-box",
    [ValidateSet("compact_only", "compact_and_exploded")]
    [string] $GenerationMode = "compact_only",
    [string] $TargetPath,
    [switch] $DryRun
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_fusion_helpers.ps1"

$root = Resolve-BgigRepoRoot -RepoRoot $RepoRoot
$target = Get-BgigFusionAddinTargetPath -TargetPath $TargetPath
$commit = Get-BgigCurrentCommit -RepoRoot $root
$cadIrPath = Join-Path $env:TEMP ("bgig-p34-sliding-lid-{0}-{1}.cad-ir.json" -f $StarterId, $commit)
$selectionPath = Join-Path $env:TEMP ("bgig-p34-sliding-lid-{0}-{1}.selection.json" -f $StarterId, $commit)

Write-Output "BGIG P34 sliding lid Fusion preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Starter: $StarterId"
Write-Output "CAD IR output: $cadIrPath"

if ($DryRun) {
    Write-Output "Dry run: would export the two-piece sliding-lid coupon."
}
else {
    $env:PYTHONPATH = Join-Path $root "src"
    & python -m board_game_insert_generator export-local-composer-selection `
        --starter $StarterId `
        --mechanism sliding_lid `
        --output $cadIrPath `
        --selection-output $selectionPath
    if ($LASTEXITCODE -ne 0) {
        throw "Sliding-lid coupon CAD IR export failed for starter: $StarterId"
    }
}

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$settings = @{
    action = "generate"
    input_mode = "cad_ir_file"
    generation_mode = $GenerationMode
    cad_ir_path = $cadIrPath
    config_json_path = ""
    project_root = $root
}
Write-BgigFusionUiSettings -TargetPath $target -Settings $settings -DryRun:$DryRun

Write-Output ""
Write-Output "Fusion actions remaining:"
Write-Output "1. Open Fusion 360 with an Assembly-compatible design and run BGIG."
Write-Output "2. Click Run with the prepared CAD IR path."
Write-Output "3. Verify the normal open trays plus one coupon beside the box: one tray and one cap."
Write-Output "4. Verify the cap is one physical body with two downward side rails, not three loose pieces."
Write-Output "5. Verify the report says Joined cap rails: 2 and Print validation: false."
Write-Output "6. Reply P34 Fusion OK if this is visible and clear, otherwise P34 Fusion KO with what you see."
Write-Output "Prepared P34 sliding lid coupon smoke test: $(-not $DryRun)"
