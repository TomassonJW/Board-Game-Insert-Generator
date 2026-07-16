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

Write-Output "BGIG P44-M007H02 focus, card measurement and sleeve estimation preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.39"') {
        throw "Installed P44-M007H02 package mismatch: expected 0.1.39."
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
        "DEFAULT_SLEEVE_EXTRA_XY_MM=3",
        "DEFAULT_SLEEVE_EXTRA_Z_MM_PER_CARD=.19",
        "ESTIMATED_CARD_THICKNESS_MM=.31",
        "card_stack_declared_thickness_mm",
        ("Nombre de cartes estim" + [char]0x00E9 + "es"),
        "sleeve_extra_xy_mm",
        "sleeve_extra_z_mm_per_card",
        'data-action="toggle-group"',
        ".group-card.is-collapsed .row-details",
        'data-bridge="materialize_project"'
    )) {
        if ($palette -notlike "*$marker*") { throw "Installed P44-M007H02 palette marker missing: $marker" }
    }
    if ($palette -like '*data-bridge="validate_project"*') {
        throw "Installed P44-M007H02 palette still exposes the obsolete Verifier action."
    }
    $materializeCount = ([regex]::Matches($palette, 'data-bridge="materialize_project"')).Count
    if ($materializeCount -ne 1) {
        throw "Installed P44-M007H02 palette must expose exactly one explicit materialize action; got $materializeCount."
    }
}

Write-Output ""
Write-Output "P44-M007H02 Fusion actions remaining:"
Write-Output "1. Remplacer rapidement la selection complete de trois champs successifs. Autosave, minima et proposition ne doivent jamais retirer focus ou selection."
Write-Output "2. Arreter la saisie. Apres environ 1,5 seconde, Apercu doit afficher uniquement les dernieres valeurs."
Write-Output "3. Ajouter le preset Cartes : son nom est Cartes et Sleeves est decoche par defaut."
Write-Output "4. Verifier que Methode de mesure est le dernier champ avant le menu ..., apres Z en Epaisseur paquet et apres Epaisseur carte en mode compte."
Write-Output "5. En Epaisseur paquet, Z est visible et Qte/Epaisseur carte sont absents. En Epaisseur carte x nb, Z est absent et Qte/Epaisseur carte sont visibles."
Write-Output "6. Activer Sleeves : Delta sleeve X/Y vaut 3 mm et Delta sleeve Z / carte vaut 0,19 mm dans les deux methodes."
Write-Output "7. En Epaisseur paquet avec Z = 24 mm, Nombre de cartes estimees affiche 77 et le resolu Z affiche 38,63 mm. Decocher Sleeves ramene le resolu Z a 24 mm."
Write-Output "8. Replier puis deplier un conteneur : son en-tete complet reste visible et seuls ses assets sont masques."
Write-Output "9. Ouvrir Apercu : statut compact et vues dessus/X-Z precedent alertes et details. Recalculer maintenant ne cree aucune scene."
Write-Output "10. Dans Reglages, Hauteur de conception est grisee, derivee et non editable."
Write-Output "11. Confirmer qu'aucune scene BGIG ne change avant un clic explicite sur Materialiser dans Fusion."
Write-Output "12. Reply: P44-M007H02 Fusion OK 0.1.39 - commit <sha>, or contextual KO. This gate does not validate physical values or printing."
Write-Output "Prepared P44-M007H02 Fusion test: $(-not $DryRun)"
