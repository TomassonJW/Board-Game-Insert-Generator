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
$cadIrPath = Join-Path $env:TEMP ("bgig-local-composer-{0}-{1}.selection.cad-ir.json" -f $StarterId, $commit)
$selectionPath = Join-Path $env:TEMP ("bgig-local-composer-{0}-{1}.selection.json" -f $StarterId, $commit)

Write-Output "BGIG local composer selection Fusion preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Starter: $StarterId"
Write-Output "Generation mode: $GenerationMode"
Write-Output "CAD IR output: $cadIrPath"
Write-Output "Selection output: $selectionPath"

if ($DryRun) {
    Write-Output "Dry run: would export the selected local composer plan as Fusion CAD IR."
}
else {
    $env:PYTHONPATH = Join-Path $root "src"
    & python -m board_game_insert_generator export-local-composer-selection `
        --starter $StarterId `
        --output $cadIrPath `
        --selection-output $selectionPath
    if ($LASTEXITCODE -ne 0) {
        throw "Local composer selection CAD IR export failed for starter: $StarterId"
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
Write-Output "1. Open Fusion 360 and an Assembly-compatible design."
Write-Output "2. Run BoardGameInsertGenerator from Utilities > Add-ins or click Generate Board Game Insert."
Write-Output "3. Confirm Input mode = cad_ir_file, Action = generate, Generation mode = $GenerationMode."
Write-Output "4. Confirm CAD IR path = $cadIrPath."
Write-Output "5. Click Run and verify exactly the selected module envelopes are created: one blank per selected tray, in compact scene positions."
Write-Output "6. Confirm no finished cavities or walls are claimed, and Print validation remains false."
Write-Output "Prepared local composer selection smoke test: $(-not $DryRun)"