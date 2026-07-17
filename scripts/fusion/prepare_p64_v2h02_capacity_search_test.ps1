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

Write-Output "BGIG P64-V2H02 capacity and search-truth product-gate preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.53"') {
        throw "Installed P64-V2H02 package mismatch: expected 0.1.53."
    }

    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        'function capacityCard(response)',
        'theoretical_remaining_volume_mm3',
        'max_participant_branches',
        'eligible_family_ids',
        'orderedBodies=[...bodyItems]',
        'cavity.parent_id===body.id'
    )) {
        if (-not $palette.Contains($marker)) {
            throw "Installed P64-V2H02 palette marker missing: $marker"
        }
    }

    $partition = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\partition_solver.py") -Raw -Encoding UTF8
    foreach ($marker in @(
        'PARTITION_CAPACITY_SCHEMA_V1',
        'def _attach_capacity_summary(',
        'necessary_volume_bound_not_packing_proof',
        'explicit_complement_volume_mm3',
        'PORTFOLIO_NO_SOLUTION_WITHIN_BUDGET'
    )) {
        if (-not $partition.Contains($marker)) {
            throw "Installed P64-V2H02 capacity marker missing: $marker"
        }
    }

    $derivation = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\container_derivation.py") -Raw -Encoding UTF8
    foreach ($marker in @('def _arrange_compartments(', 'bounded_shelf_candidates_v2')) {
        if (-not $derivation.Contains($marker)) {
            throw "Installed P64-V2H02 derivation marker missing: $marker"
        }
    }

    $greedy = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\free_3d_greedy_solver.py") -Raw -Encoding UTF8
    foreach ($marker in @('def _initial_extreme_points(', 'def _xy_rectangles_overlap(', 'rotation_deg_z')) {
        if (-not $greedy.Contains($marker)) {
            throw "Installed P64-V2H02 reservation marker missing: $marker"
        }
    }

    $beam = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\free_3d_beam_solver.py") -Raw -Encoding UTF8
    foreach ($marker in @('A valid body may bridge several lower supports', '_initial_extreme_points(initial_spaces, inset_zones)')) {
        if (-not $beam.Contains($marker)) {
            throw "Installed P64-V2H02 beam marker missing: $marker"
        }
    }

    $portfolio = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\solver_portfolio.py") -Raw -Encoding UTF8
    foreach ($marker in @('beam=(8, 2, 1_000', 'beam=(24, 6, 5_000', 'beam=(64, 12, 15_000')) {
        if (-not $portfolio.Contains($marker)) {
            throw "Installed P64-V2H02 effort marker missing: $marker"
        }
    }
}

Write-Output ""
Write-Output "P64-V2H02 Fusion actions remaining:"
Write-Output "1. Reload add-in 0.1.53. Open a simple solvable project and confirm that Capacity shows usable volume, minimum envelopes and theoretical remaining volume."
Write-Output "2. Return to the preserved dense project. Recalculate with Free 3D + Deep. A non-certified result must say unresolved within budget, not impossible, and must still show the theoretical capacity bound."
Write-Output "3. Compare Quick, Normal and Deep diagnostics: max placement orders must be 1, 2 and 4; beam widths must be 8, 24 and 64. Identical final outcomes are allowed."
Write-Output "4. Compare Auto intelligent and Free 3D. Their strategy chains must differ in the diagnostic even when the same best result or status is returned."
Write-Output "5. Inspect Top view: upper bodies must mask cavities below them. The side cut remains unchanged."
Write-Output "6. Confirm that no Fusion body changes before Materialize in Fusion. This gate validates no physical value and no print."
Write-Output "7. Reply: P64-V2H02 Fusion OK 0.1.53 - commit $commit, or contextual KO with method, effort, capacity and diagnostic."
Write-Output "Prepared P64-V2H02 Fusion test: $(-not $DryRun)"