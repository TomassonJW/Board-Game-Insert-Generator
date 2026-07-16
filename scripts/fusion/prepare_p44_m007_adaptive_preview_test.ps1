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

Write-Output "BGIG P44-M007 adaptive preview preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.37"') {
        throw "Installed P44-M007 package mismatch: expected 0.1.37."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        "DERIVE_DEBOUNCE_MS=350",
        "AUTO_SOLVE_STABILITY_MS=1500",
        "latestDerivedRequest",
        "scheduleAdaptiveSolve",
        "Recalculer maintenant",
        'id="preview-status"',
        'id="preview-explanations"',
        ("Calcul" + [char]0x00E9 + "e automatiquement"),
        'id="design-height" readonly aria-readonly="true" tabindex="-1"',
        'data-bridge="materialize_project"'
    )) {
        if ($palette -notlike "*$marker*") { throw "Installed P44-M007 palette marker missing: $marker" }
    }
    if ($palette -like '*data-bridge="validate_project"*') {
        throw "Installed P44-M007 palette still exposes the obsolete Vérifier action."
    }
    $materializeCount = ([regex]::Matches($palette, 'data-bridge="materialize_project"')).Count
    if ($materializeCount -ne 1) {
        throw "Installed P44-M007 palette must expose exactly one explicit materialize action; got $materializeCount."
    }
}

Write-Output ""
Write-Output "P44-M007 Fusion actions remaining:"
Write-Output "1. Open BGIG and rapidly change several dimensions. The lifecycle must move through stabilisation/minima/proposition without stealing focus or scrolling the active field."
Write-Output "2. Stop editing. After roughly 1.5 seconds, Aperçu must update automatically from the latest values only."
Write-Output "3. Open Aperçu. The compact status and the top/X-Z views must appear before alerts and detailed metrics."
Write-Output "4. Change a value again. The old proposal must be marked obsolete, then replaced by the current automatic proposal."
Write-Output "5. Use Recalculer maintenant once as a manual fallback. It must refresh the proposal without creating or updating a Fusion scene."
Write-Output "6. In Réglages, Hauteur de conception must be visibly grey, derived and impossible to edit."
Write-Output "7. Confirm that no BGIG scene changes before an explicit click on Matérialiser dans Fusion."
Write-Output "8. Reply: P44-M007 Fusion OK 0.1.37 - commit <sha>, or contextual KO. This gate does not validate physical values or printing."
Write-Output "Prepared P44-M007 Fusion test: $(-not $DryRun)"
