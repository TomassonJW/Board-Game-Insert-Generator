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

Write-Output "BGIG P64-H02 diversified fallback and inline actions preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.44"') {
        throw "Installed P64-H02 package mismatch: expected 0.1.44."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        "child-inline-actions",
        'class="child-inline-actions">${moveAction}${deleteAction}</div>'
    )) {
        if ($palette -notlike "*$marker*") {
            throw "Installed P64-H02 palette marker missing: $marker"
        }
    }
    $partition = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\partition_solver.py") -Raw -Encoding UTF8
    foreach ($marker in @(
        "MAX_DIVERSIFIED_PORTFOLIOS = 6",
        "_DIVERSIFIED_RETRY_CODES",
        "def _finalize_portfolio_search("
    )) {
        if ($partition -notlike "*$marker*") {
            throw "Installed P64-H02 partition marker missing: $marker"
        }
    }
    $solver = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\volumetric_stage_solver.py") -Raw -Encoding UTF8
    if ($solver -notlike "*diversified_order_seed*") {
        throw "Installed P64-H02 diversified order marker missing."
    }
}

Write-Output ""
Write-Output "P64-H02 Fusion actions remaining:"
Write-Output "1. Recharger l add-in et conserver le projet problematique laisse ouvert, sans modifier ses dimensions."
Write-Output "2. Dans chaque ligne d element, verifier que la croix est sur la meme ligne que le menu ..., immediatement a sa droite."
Write-Output "3. Cliquer Recalculer maintenant : le projet doit redevenir constructible, avec ses 8 conteneurs places sur 2 niveaux, sans TOP_INSET_PIERCES_CAVITY_FLOOR ni Calcul impossible."
Write-Output "4. Modifier ou ajouter un petit element, puis verifier que le recalcul reste courant et constructible."
Write-Output "5. Confirmer qu aucune scene BGIG ne change avant Materialiser dans Fusion."
Write-Output "6. Reply: P64-H02 Fusion OK 0.1.44 - commit $commit, or contextual KO. This gate does not validate physical values or printing."
Write-Output "Prepared P64-H02 Fusion test: $(-not $DryRun)"
