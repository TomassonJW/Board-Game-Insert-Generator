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

Write-Output "BGIG P44-VH01 design-height and multi-stage preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.41"') {
        throw "Installed P44-VH01 package mismatch: expected 0.1.41."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        "function designHeightValue()",
        "function syncDesignHeight()",
        "project.box.usable_height_mm=Math.max(0.0001,designHeightValue())",
        "if(path==='box.inner_dimensions_mm.z')syncDesignHeight()",
        "if(name==='container_box_z')syncDesignHeight()",
        'id="design-height" readonly aria-readonly="true" tabindex="-1"',
        'data-bridge="materialize_project"'
    )) {
        if ($palette -notlike "*$marker*") { throw "Installed P44-VH01 palette marker missing: $marker" }
    }
}

Write-Output ""
Write-Output "P44-VH01 Fusion actions remaining:"
Write-Output "1. Rouvrir le projet contextuel avec les plateaux/livrets et les nombreux conteneurs."
Write-Output "2. Modifier Z de boite. Hauteur de conception doit suivre Z moins le jeu Z conteneur-boite."
Write-Output "3. Avec une hauteur volontairement tres grande, Recalculer maintenant doit produire plusieurs etages au lieu de conserver les anciennes erreurs de fond sous plateau."
Write-Output "4. Remettre une hauteur realiste et confirmer que tout refus restant correspond a cette hauteur reelle."
Write-Output "5. Confirmer qu aucune scene BGIG ne change avant Materialiser dans Fusion."
Write-Output "6. Reply: P44-VH01 Fusion OK 0.1.41 - commit $commit, or contextual KO. This gate does not validate physical values or printing."
Write-Output "Prepared P44-VH01 Fusion test: $(-not $DryRun)"
