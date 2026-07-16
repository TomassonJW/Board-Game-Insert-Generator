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

Write-Output "BGIG P64-H01 balanced dense solver preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.42"') {
        throw "Installed P64-H01 package mismatch: expected 0.1.42."
    }
    $solver = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\volumetric_stage_solver.py") -Raw -Encoding UTF8
    foreach ($marker in @(
        "MAX_ADAPTIVE_STAGE_COUNTS = 8",
        "def _adaptive_stage_partition(",
        'stage_height if preference == "balanced" else None',
        '"spatial_balance": _round(spatial)',
        '"stage_load_balance": _round(stage_load_balance)'
    )) {
        if ($solver -notlike "*$marker*") {
            throw "Installed P64-H01 solver marker missing: $marker"
        }
    }
}

Write-Output ""
Write-Output "P64-H01 Fusion actions remaining:"
Write-Output "1. Rouvrir le projet dense reel avec environ 30 conteneurs et 77 elements, en preference Equilibre."
Write-Output "2. Conserver une hauteur utile realiste proche de 183 mm, puis ajouter le petit asset qui faisait basculer le calcul en impossible."
Write-Output "3. Le calcul doit rester constructible et proposer plusieurs niveaux Z ; aucun ancien diagnostic de faux manque de volume ne doit revenir."
Write-Output "4. Observer que la repartition utilise progressivement Z et ne concentre pas tout sur un seul etage XY quand une composition 3D plus equilibree existe."
Write-Output "5. Modifier encore un petit asset dans un bac charge : le recalcul doit rester courant, coherent et sans resultat ancien."
Write-Output "6. Confirmer qu aucune scene BGIG ne change avant Materialiser dans Fusion."
Write-Output "7. Reply: P64-H01 Fusion OK 0.1.42 - commit $commit, or contextual KO. This gate does not validate physical values or printing."
Write-Output "Prepared P64-H01 Fusion test: $(-not $DryRun)"
