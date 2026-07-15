param(
    [string] $RepoRoot,
    [string] $TargetPath,
    [switch] $DryRun
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_fusion_helpers.ps1"

$root = Resolve-BgigRepoRoot -RepoRoot $RepoRoot
$target = Get-BgigFusionAddinTargetPath -TargetPath $TargetPath
$commit = Get-BgigCurrentCommit -RepoRoot $root

Write-Output "BGIG P44-M006 document cycle preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.29"') {
        throw "Installed P44-M006 package mismatch: expected 0.1.29."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        'id="document-status"',
        'id="save-document-action"',
        'data-action="open-project"',
        'data-action="save-project-as"',
        'id="design-height"',
        'id="diagnostic-tools"',
        'bgig_palette_document'
    )) {
        if ($palette -notlike "*$marker*") { throw "Installed P44-M006 palette marker missing: $marker" }
    }
    $entrypoint = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.py") -Raw -Encoding UTF8
    if ($entrypoint -notlike "*createFileDialog()*") {
        throw "Installed P44-M006 native document dialog is missing."
    }
}

Write-Output ""
Write-Output "P44-M006 Fusion actions remaining:"
Write-Output "1. Open BGIG and check visible design settings, derived design height, and collapsed diagnostics."
Write-Output "2. Use New then Save As. Check Fusion native dialog, default BGIG projects folder, cancel safety, and displayed filename."
Write-Output "3. Change one value, wait two seconds, close and reopen BGIG. Check local recovery."
Write-Output "4. Open a BGIG JSON file and then a recent project. The source file must not be rewritten automatically."
Write-Output "5. Inspect and clear only inside diagnostics; clear must ask confirmation. No calculation or scene update starts by itself."
Write-Output "6. Reply: P44-M006 Fusion OK 0.1.29 - commit <sha>, or contextual KO."
Write-Output "Prepared P44-M006 Fusion test: $(-not $DryRun)"
