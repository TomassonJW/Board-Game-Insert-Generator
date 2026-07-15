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
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.30"') {
        throw "Installed P44-M006 package mismatch: expected 0.1.30."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        'id="document-status"',
        'id="save-document-action"',
        'data-action="open-project"',
        'data-action="save-project-as"',
        'id="design-height"',
        'id="diagnostic-tools"',
        'bgig_palette_document',
        'hasUnsavedEdition',
        "if(sceneSummary)sceneSummary.textContent"
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
Write-Output "1. Open BGIG, then Inspecter la scène. No TypeError may appear; the diagnostic response remains readable."
Write-Output "2. Modify one value and click Nouveau. A confirmation must appear; cancel keeps the current edition."
Write-Output "3. Enregistrer sous, then click Nouveau without a new edit. It must create a clean unnamed project without overwriting the named file."
Write-Output "4. Change one value, wait two seconds, close and reopen BGIG. Check local recovery."
Write-Output "5. Open a BGIG JSON file and then a recent project. The source file must not be rewritten automatically."
Write-Output "6. Clear only inside diagnostics; clear must ask confirmation. No calculation or scene update starts by itself."
Write-Output "7. Reply: P44-M006 Fusion OK 0.1.30 - commit <sha>, or contextual KO."
Write-Output "Prepared P44-M006 Fusion test: $(-not $DryRun)"
