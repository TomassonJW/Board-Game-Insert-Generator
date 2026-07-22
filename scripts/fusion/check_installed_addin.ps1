param(
    [string] $TargetPath,
    [string] $ExpectedVersion
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_fusion_helpers.ps1"

$target = Get-BgigFusionAddinTargetPath -TargetPath $TargetPath
Write-Output "BGIG installed Fusion add-in check"
Write-Output "Target: $target"

if (-not (Test-Path -LiteralPath $target -PathType Container)) {
    throw "Installed add-in folder not found: $target"
}

$entrypoint = Join-Path $target "BoardGameInsertGenerator.py"
$manifest = Join-Path $target "BoardGameInsertGenerator.manifest"
$settings = Join-Path $target "bgig_ui_settings.json"
if (-not (Test-Path -LiteralPath $manifest -PathType Leaf)) {
    throw "Installed add-in manifest missing: $manifest"
}
$manifestText = Get-Content -LiteralPath $manifest -Raw -Encoding UTF8
$versionMatch = [regex]::Match($manifestText, '"version"\s*:\s*"(?<version>[^"]+)"')
if (-not $versionMatch.Success) {
    throw "Installed add-in manifest has no readable version: $manifest"
}
$manifestVersion = $versionMatch.Groups["version"].Value
if ($ExpectedVersion -and $manifestVersion -ne $ExpectedVersion) {
    throw "Installed add-in package version mismatch: expected $ExpectedVersion, got $manifestVersion."
}

Assert-BgigFusionAddinMarkers -AddinPath $target
Assert-BgigPaletteProjectRuntime -AddinPath $target

Write-Output "Entrypoint: $entrypoint"
Write-Output "Manifest exists: $(Test-Path -LiteralPath $manifest -PathType Leaf)"
Write-Output "Manifest version: $manifestVersion"
Write-Output "Settings exists: $(Test-Path -LiteralPath $settings -PathType Leaf)"
Write-Output "Runtime package and marker check: ok"
