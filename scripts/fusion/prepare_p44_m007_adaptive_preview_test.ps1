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

Write-Output "BGIG P44-M007H01 focus, cards and collapsible containers preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.38"') {
        throw "Installed P44-M007H01 package mismatch: expected 0.1.38."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        "DERIVE_DEBOUNCE_MS=350",
        "AUTO_SOLVE_STABILITY_MS=1500",
        "latestDerivedRequest",
        "scheduleAdaptiveSolve",
        "renderBackgroundUpdate(action)",
        "deferredDerivedPaint",
        "Recalculer maintenant",
        'id="preview-status"',
        'id="preview-explanations"',
        ("Calcul" + [char]0x00E9 + "e automatiquement"),
        'id="design-height" readonly aria-readonly="true" tabindex="-1"',
        ("M" + [char]0x00E9 + "thode de mesure"),
        ("Epaisseur paquet").Replace("E", [char]0x00C9),
        ("Epaisseur carte " + [char]0x00D7 + " nb").Replace("E", [char]0x00C9),
        "sleeve_extra_xy_mm",
        "sleeve_extra_z_mm_per_card",
        'data-action="toggle-group"',
        ".group-card.is-collapsed .row-details",
        'data-bridge="materialize_project"'
    )) {
        if ($palette -notlike "*$marker*") { throw "Installed P44-M007H01 palette marker missing: $marker" }
    }
    if ($palette -like '*data-bridge="validate_project"*') {
        throw "Installed P44-M007H01 palette still exposes the obsolete Verifier action."
    }
    $materializeCount = ([regex]::Matches($palette, 'data-bridge="materialize_project"')).Count
    if ($materializeCount -ne 1) {
        throw "Installed P44-M007H01 palette must expose exactly one explicit materialize action; got $materializeCount."
    }
}

Write-Output ""
Write-Output "P44-M007H01 Fusion actions remaining:"
Write-Output "1. Select the full value of one numeric field, type its replacement, immediately select and type in two other fields. Autosave, minima and proposal responses must never remove focus or the active selection."
Write-Output "2. Stop editing. After roughly 1.5 seconds, Apercu must update automatically from the latest values only."
Write-Output "3. For a Cards asset, confirm that Methode de mesure appears in the primary row between Forme and X."
Write-Output "4. Select Epaisseur paquet: Z is visible; Qte and Epaisseur carte are absent. Select Epaisseur carte x nb: Z is absent; Qte and Epaisseur carte are visible."
Write-Output "5. Enable Sleeves: Delta sleeve X/Y is visible; in count mode Delta sleeve Z / carte is also visible and both remain editable."
Write-Output "6. Replier puis deplier un conteneur: its header, count, minimum, mode, thicknesses, add and delete controls remain visible while its assets are hidden only when collapsed."
Write-Output "7. Open Apercu. The compact status and the top/X-Z views must appear before alerts and detailed metrics."
Write-Output "8. Use Recalculer maintenant once as a manual fallback. It must refresh the proposal without creating or updating a Fusion scene."
Write-Output "9. In Reglages, Hauteur de conception must be visibly grey, derived and impossible to edit."
Write-Output "10. Confirm that no BGIG scene changes before an explicit click on Materialiser dans Fusion."
Write-Output "11. Reply: P44-M007H01 Fusion OK 0.1.38 - commit <sha>, or contextual KO. This gate does not validate physical values or printing."
Write-Output "Prepared P44-M007H01 Fusion test: $(-not $DryRun)"
