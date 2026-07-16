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

Write-Output "BGIG P44-M007H03 container folding and card sleeve resolution preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.40"') {
        throw "Installed P44-M007H03 package mismatch: expected 0.1.40."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        "DERIVE_DEBOUNCE_MS=350",
        "AUTO_SOLVE_STABILITY_MS=1500",
        "latestDerivedRequest",
        "scheduleAdaptiveSolve",
        "renderBackgroundUpdate(action)",
        "deferredDerivedPaint",
        "derivedStale=true",
        "markCardFactsPending",
        ("A recalculer").Replace("A", [char]0x00C0),
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
        "card_declared_xy_mm",
        "Nb cartes",
        "sleeve_extra_xy_mm",
        "sleeve_extra_z_mm_per_card",
        'data-action="toggle-group"',
        'data-action="toggle-all-groups"',
        "function toggleAllGroups()",
        ".group-card.is-collapsed .row-details",
        ".asset-card-options .card-option-strip{display:flex",
        ('placeholder="D' + [char]0x00E9 + 'faut"'),
        'data-bridge="materialize_project"'
    )) {
        if ($palette -notlike "*$marker*") { throw "Installed P44-M007H03 palette marker missing: $marker" }
    }
    foreach ($obsolete in @('data-bridge="validate_project"', 'data-density=', 'setDensity(', 'bgig-list-density', 'compact-summary')) {
        if ($palette -like "*$obsolete*") {
            throw "Installed P44-M007H03 palette still exposes obsolete UI behavior: $obsolete"
        }
    }
    $materializeCount = ([regex]::Matches($palette, 'data-bridge="materialize_project"')).Count
    if ($materializeCount -ne 1) {
        throw "Installed P44-M007H03 palette must expose exactly one explicit materialize action; got $materializeCount."
    }
}

Write-Output ""
Write-Output "P44-M007H03 Fusion actions remaining:"
Write-Output "1. Remplacer rapidement la selection complete de trois champs successifs. Autosave, minima et proposition ne doivent jamais retirer focus ou selection."
Write-Output "2. Pendant le recalcul, le fait carte doit indiquer A recalculer au lieu de conserver une ancienne valeur. Apres stabilisation, Apercu et Resolu doivent refleter uniquement la derniere saisie."
Write-Output "3. Confirmer que Compact et Detaille ont disparu, puis utiliser le bouton discret a droite de Conteneurs pour replier et deplier tous les conteneurs."
Write-Output "4. Confirmer que chaque conteneur reste repliable seul et que sa ligne principale reste visible. Les champs vides Epaisseur paroi et Epaisseur fond indiquent Defaut."
Write-Output "5. Ajouter le preset Cartes : son nom est Cartes, Sleeves est decoche par defaut, et les controles cartes tiennent sur une ligne large avec Resolu."
Write-Output "6. En dimensions manuelles, saisir X=66, Y=88, Z=27, activer Sleeves, Delta X/Y=3 et Delta Z/carte=0,19 : Nb cartes doit afficher 87 et Resolu 69 x 91 x 43,53 mm."
Write-Output "7. Decocher Sleeves : Resolu doit revenir a 66 x 88 x 27 mm sans cumul ni valeur ancienne."
Write-Output "8. En Epaisseur paquet, Z est visible et Qte/Epaisseur carte sont absents. En Epaisseur carte x nb, Z est absent et Qte/Epaisseur carte sont visibles."
Write-Output "9. Ouvrir Apercu : statut compact et vues dessus/X-Z precedent alertes et details. Recalculer maintenant ne cree aucune scene."
Write-Output "10. Dans Reglages, Hauteur de conception est grisee, derivee et non editable. Confirmer qu'aucune scene BGIG ne change avant un clic explicite sur Materialiser dans Fusion."
Write-Output "11. Reply: P44-M007H03 Fusion OK 0.1.40 - commit <sha>, or contextual KO. This gate does not validate physical values or printing."
Write-Output "Prepared P44-M007H03 Fusion test: $(-not $DryRun)"
