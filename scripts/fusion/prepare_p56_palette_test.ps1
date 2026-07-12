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

Write-Output "BGIG P56 Fusion-only palette preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
}

Write-Output ""
Write-Output "P56 Fusion actions remaining:"
Write-Output "1. Ouvre Fusion 360 et lance BoardGameInsertGenerator. Aucun navigateur ne doit s ouvrir."
Write-Output "2. Verifie les six vues Boite, Pieces, Plateaux, Bacs, Fabrication et Resultat."
Write-Output "3. Ajoute un bac, une famille de pieces et un livret ; duplique puis supprime une piece."
Write-Output "4. Active Mode avance et verifie jeux, axes extensibles et dimensions verrouillees."
Write-Output "5. Clique Verifier : Resultat doit afficher le contrat P55 et zero corps automatique."
Write-Output "6. Clique Sauvegarder, ferme puis rouvre l add-in : le projet doit etre repris."
Write-Output "7. Mets une dimension obligatoire a zero et verifie une erreur francaise actionnable, puis corrige-la."
Write-Output "8. Reponds P56 Fusion OK, ou P56 Fusion KO avec l etape et le message visibles."
Write-Output "Prepared P56 Fusion-only palette smoke test: $(-not $DryRun)"
