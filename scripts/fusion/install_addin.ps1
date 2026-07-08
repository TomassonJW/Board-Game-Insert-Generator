param(
    [string] $RepoRoot,
    [string] $TargetPath,
    [switch] $DryRun
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_fusion_helpers.ps1"

$root = Resolve-BgigRepoRoot -RepoRoot $RepoRoot
$source = Get-BgigAddinSourcePath -RepoRoot $root
$target = Get-BgigFusionAddinTargetPath -TargetPath $TargetPath
$commit = Get-BgigCurrentCommit -RepoRoot $root

Write-Output "BGIG Fusion add-in install"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Source: $source"
Write-Output "Target: $target"

Assert-BgigFusionAddinMarkers -AddinPath $source
Copy-BgigFusionAddin -SourcePath $source -TargetPath $target -DryRun:$DryRun

if (-not $DryRun) {
    Assert-BgigFusionAddinMarkers -AddinPath $target
}

Write-Output "Installed add-in: $(-not $DryRun)"
if ($DryRun) {
    Write-Output "Dry run complete. No AppData files were changed."
}
