param(
    [string] $TargetPath
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_fusion_helpers.ps1"

$target = Get-BgigFusionAddinTargetPath -TargetPath $TargetPath
Write-Output "BGIG installed Fusion add-in check"
Write-Output "Target: $target"

if (-not (Test-Path -LiteralPath $target -PathType Container)) {
    throw "Installed add-in folder not found: $target"
}

Assert-BgigFusionAddinMarkers -AddinPath $target

$entrypoint = Join-Path $target "BoardGameInsertGenerator.py"
$manifest = Join-Path $target "BoardGameInsertGenerator.manifest"
$settings = Join-Path $target "bgig_ui_settings.json"

Write-Output "Entrypoint: $entrypoint"
Write-Output "Manifest exists: $(Test-Path -LiteralPath $manifest -PathType Leaf)"
Write-Output "Settings exists: $(Test-Path -LiteralPath $settings -PathType Leaf)"
Write-Output "Marker check: ok"
