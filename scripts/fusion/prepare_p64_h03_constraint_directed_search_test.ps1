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

Write-Output "BGIG P64-H03 constraint-directed dense search preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.45"') {
        throw "Installed P64-H03 package mismatch: expected 0.1.45."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        "child-inline-actions",
        'class="child-inline-actions">${moveAction}${deleteAction}</div>'
    )) {
        if ($palette -notlike "*$marker*") {
            throw "Installed P64-H03 palette marker missing: $marker"
        }
    }
    $partition = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\partition_solver.py") -Raw -Encoding UTF8
    foreach ($marker in @(
        "def _structured_retry_strategies(",
        "top_inset_search_context",
        "directed_portfolios_evaluated"
    )) {
        if ($partition -notlike "*$marker*") {
            throw "Installed P64-H03 partition marker missing: $marker"
        }
    }
    $solver = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\volumetric_stage_solver.py") -Raw -Encoding UTF8
    foreach ($marker in @(
        "STRUCTURED_ORDER_STRATEGIES",
        "def _beam_stack_partitions(",
        "def _rebalance_stack_top_height_for_inset(",
        "def _layout_top_inset_penalty("
    )) {
        if ($solver -notlike "*$marker*") {
            throw "Installed P64-H03 constraint-directed marker missing: $marker"
        }
    }
}

Write-Output ""
Write-Output "P64-H03 Fusion actions remaining:"
Write-Output "1. Recharger l add-in et conserver le projet problematique laisse ouvert, sans modifier ses dimensions."
Write-Output "2. Cliquer Recalculer maintenant : le projet doit redevenir constructible sans TOP_INSET_PIERCES_CAVITY_FLOOR ni Calcul impossible."
Write-Output "3. Ajouter le petit asset qui provoquait le faux impossible ; le calcul doit rester courant et constructible."
Write-Output "4. Ajouter ensuite plusieurs assets puis plusieurs conteneurs : la recherche doit creer ou reorganiser les etages sans faux impossible tant qu une solution valide existe."
Write-Output "5. Verifier que les actions ... et X restent alignees sur la meme ligne."
Write-Output "6. Confirmer qu aucune scene BGIG ne change avant Materialiser dans Fusion."
Write-Output "7. Trial reply before commit: P64-H03 Fusion trial OK 0.1.45 (uncommitted), or contextual KO. This trial does not validate physical values or printing."
Write-Output "Prepared P64-H03 Fusion test: $(-not $DryRun)"
