param(
    [string] $RepoRoot,
    [string] $TargetPath,
    [switch] $DryRun
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_fusion_helpers.ps1"
$root = Resolve-BgigRepoRoot -RepoRoot $RepoRoot
$target = Get-BgigFusionAddinTargetPath -TargetPath $TargetPath

Write-Output "BGIG P44-V foundation UX preparation"
Write-Output "Product package baseline: 0.1.40 / 92f07c8"
& "$PSScriptRoot\prepare_p44_m007_adaptive_preview_test.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.40"') { throw "Installed P44-V package mismatch: expected 0.1.40." }
}
Write-Output "P44-V Fusion actions remaining: run docs/P44_V_FOUNDATION_UX_GATE.md"
Write-Output "Reply: P44-V Fusion OK 0.1.40 - package 92f07c8, or contextual KO."
