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

Write-Output "BGIG P44-VH02 direct deletion and unique names preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.43"') {
        throw "Installed P44-VH02 package mismatch: expected 0.1.43."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        "child-delete-action",
        "function nextUniqueGroupName(requestedName)",
        "project.contents=project.contents.filter(content=>content.container_group_id!==group.id)"
    )) {
        if ($palette -notlike "*$marker*") {
            throw "Installed P44-VH02 palette marker missing: $marker"
        }
    }
}

Write-Output ""
Write-Output "P44-VH02 Fusion actions remaining:"
Write-Output "1. Ajouter deux elements dans un meme conteneur et verifier que la croix visible est placee a cote du menu ... de chaque element."
Write-Output "2. Supprimer un element par cette croix et verifier que seul cet element disparait."
Write-Output "3. Tenter de supprimer un conteneur non vide, choisir Annuler et verifier qu aucun contenu ni conteneur ne change."
Write-Output "4. Recommencer, confirmer, puis verifier que le conteneur et tous ses elements disparaissent ensemble."
Write-Output "5. Creer plusieurs conteneurs portant le meme nom et verifier les suffixes incrementaux (par exemple Nouveau bac, Nouveau bac 2, Nouveau bac 3)."
Write-Output "6. Confirmer qu aucune scene BGIG ne change avant Materialiser dans Fusion."
Write-Output "7. Reply: P44-VH02 Fusion OK 0.1.43 - commit $commit, or contextual KO. This gate does not validate physical values or printing."
Write-Output "Prepared P44-VH02 Fusion test: $(-not $DryRun)"
