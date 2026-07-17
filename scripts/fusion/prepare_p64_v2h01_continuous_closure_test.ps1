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

Write-Output "BGIG P64-V2H01 continuous closure product-gate preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.52"') {
        throw "Installed P64-V2H01 package mismatch: expected 0.1.52."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        'id="solver-method"',
        'id="solver-effort"',
        'id="solver-ranking"',
        'save_solver_settings',
        'function solverTelemetryDetails',
        'renderBackgroundUpdate(action)'
    )) {
        if (-not $palette.Contains($marker)) {
            throw "Installed P64-H08 palette marker missing: $marker"
        }
    }
    $bridge = Get-Content -LiteralPath (Join-Path $target "palette_project.py") -Raw -Encoding UTF8
    foreach ($marker in @('"save_solver_settings"', 'solver_method=solver_settings["method"]', 'effort_profile=solver_settings["effort"]')) {
        if (-not $bridge.Contains($marker)) {
            throw "Installed P64-H08 bridge marker missing: $marker"
        }
    }
    $solver = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\partition_solver.py") -Raw -Encoding UTF8
    foreach ($marker in @('def solve_partition_plan(', 'solver_method: str | None = None', 'def _portfolio_public_plan(')) {
        if (-not $solver.Contains($marker)) {
            throw "Installed P64-H08 solver marker missing: $marker"
        }
    }
    $closure = Get-Content -LiteralPath (Join-Path $target "lib/board_game_insert_generator/free_3d_continuous_closure.py") -Raw -Encoding UTF8
    foreach ($marker in @('FREE_3D_CONTINUOUS_CLOSURE_VERSION', 'def close_free_3d_residual(', 'aligned_face_count')) {
        if (-not $closure.Contains($marker)) {
            throw "Installed P64-V2H01 closure marker missing: $marker"
        }
    }
    $beam = Get-Content -LiteralPath (Join-Path $target "lib/board_game_insert_generator/free_3d_beam_solver.py") -Raw -Encoding UTF8
    foreach ($marker in @('TopInsetZone', 'beam_feasible_geometry_found', 'bgig.free_3d_beam.v2')) {
        if (-not $beam.Contains($marker)) {
            throw "Installed P64-V2H01 beam marker missing: $marker"
        }
    }
}

Write-Output ""
Write-Output "P64-V2H01 Fusion actions remaining:"
Write-Output "1. Recharger l add-in 0.1.52 et conserver le projet dense actuellement ouvert, sans modifier ses dimensions."
Write-Output "2. Choisir Placement 3D libre + Approfondi, puis Recalculer maintenant : les 9 conteneurs doivent devenir materialisables, sans Calcul impossible ni erreur de cavite sous plateau."
Write-Output "3. Le diagnostic doit retenir free_3d_beam. Le plan doit utiliser plusieurs niveaux et des faces alignees ; aucune fausse harmonisation modulaire n est revendiquee."
Write-Output "4. Choisir Etages et piles : ce meme cas peut rester sans solution dans le budget. Revenir a Placement 3D libre puis Auto intelligent : les deux doivent retrouver une solution certifiee. Cela confirme que les methodes sont reellement distinctes."
Write-Output "5. Verifier que les grands bacs incompatibles avec les encastrements plateau/livret restent hors de leur empreinte, tandis que les corps compatibles peuvent atteindre le sommet et recevoir les coupes."
Write-Output "6. Confirmer qu aucun corps Fusion ne change avant Materialiser dans Fusion. Cette gate ne valide ni valeurs physiques ni impression."
Write-Output "7. Reply: P64-V2H01 Fusion OK 0.1.52 - commit $commit, or contextual KO with method, effort and diagnostic."
Write-Output "Prepared P64-V2H01 Fusion test: $(-not $DryRun)"