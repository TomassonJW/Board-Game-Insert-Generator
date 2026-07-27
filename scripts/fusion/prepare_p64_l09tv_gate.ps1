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
$python = (Get-Command python -ErrorAction Stop).Source
$preflight = Join-Path $root "scripts\fusion\p64_l09tv_preflight.py"
$localReplay = Join-Path $root "scripts\fusion\p64_l09t_local_replay.py"
$manifestPath = Join-Path $root "fusion_addin\BoardGameInsertGenerator\BoardGameInsertGenerator.manifest"
$projectDirectory = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "BGIG\projects"
$fixtureName = "p64-l09tv-01-explicit-composite.bgig.json"
$summaryName = "p64-l09tv-preflight-summary.json"
$summaryPath = Join-Path $projectDirectory $summaryName
$localReceiptPath = Join-Path $projectDirectory "p64-l09tv-local-replay-summary.json"
$documentStatePath = Join-Path $projectDirectory "bgig_document_state_v1.json"
$commitMarker = Join-Path $target "bgig_installed_commit.txt"
$workspaceTemp = Join-Path $root ".codex-work\p64-l09tv-fusion-gate"
$tempSummary = Join-Path $workspaceTemp $summaryName
$tempLocalReceipt = Join-Path $workspaceTemp "p64-l09tv-local-replay-summary.json"
$tempFixture = Join-Path $workspaceTemp $fixtureName

foreach ($required in @($preflight, $localReplay, $manifestPath)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "P64-L09T-V required source missing: $required"
    }
}
$manifestText = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8
$versionMatch = [regex]::Match($manifestText, '"version"\s*:\s*"(?<version>[^\"]+)"')
if (-not $versionMatch.Success) {
    throw "Source add-in manifest has no readable version: $manifestPath"
}
$expectedVersion = $versionMatch.Groups["version"].Value
if ($expectedVersion -ne "0.1.70") {
    throw "P64-L09T-V package version mismatch: expected 0.1.70, got $expectedVersion."
}

Write-Output "BGIG P64-L09T-V Fusion gate preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Package version: $expectedVersion"
Write-Output "Target: $target"

$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = ".;$(Join-Path $root 'src')"
    foreach ($pattern in @(
        "test_certified_plan_witness.py",
        "test_staged_calculation.py",
        "test_floor_maxrects_solver.py",
        "test_reserved_floor_stack_solver.py",
        "test_top_inset_reservation.py",
        "test_xy_composite_closure.py",
        "test_p64_l09t_f_composite_cad.py",
        "test_partition_cad.py",
        "test_fusion_palette_project.py",
        "test_fusion_palette_dom.py",
        "test_palette_worker.py",
        "test_p64_l09t_g_release_gate.py"
    )) {
        & $python -m unittest discover -s (Join-Path $root "tests") -p $pattern
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    if (-not $DryRun) {
        New-Item -ItemType Directory -Force -Path $workspaceTemp | Out-Null
    }
    if ($DryRun) {
        & $python $localReplay
    }
    else {
        & $python $localReplay --write-summary $tempLocalReceipt
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if ($DryRun) {
        & $python $preflight
    }
    else {
        & $python $preflight --output-directory $workspaceTemp --write-summary $tempSummary
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    $env:PYTHONPATH = $previousPythonPath
}

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$settings = @{
    action = "inspect"
    input_mode = "quick_parametric_box"
    generation_mode = "compact_only"
    project_root = $root
}
Write-BgigFusionUiSettings -TargetPath $target -Settings $settings -DryRun:$DryRun

if ($DryRun) {
    Write-Output "Dry run: would install the P64-L09T-V public fixture and receipts."
    Write-Output "Dry run: would preserve existing document state and colliding fixtures."
    Write-Output "Dry run: would select calculation Normal and finishing Normal."
    Write-Output "Dry run: would write the exact integrated commit marker."
}
else {
    try {
        Assert-BgigPaletteProjectRuntime -AddinPath $target
        & "$PSScriptRoot\check_installed_addin.ps1" -TargetPath $target -ExpectedVersion $expectedVersion
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

        $installedWorker = Get-Content -LiteralPath (Join-Path $target "palette_worker.py") -Raw -Encoding UTF8
        foreach ($marker in @("solve_project", "finalize_project", "source_identity_changed", "worker_pure_data_only")) {
            if (-not $installedWorker.Contains($marker)) {
                throw "Installed P64-L09T-V worker marker missing: $marker"
            }
        }
        if ($installedWorker.Contains("import adsk")) {
            throw "Installed P64-L09T-V worker imports adsk."
        }

        $installedStaged = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\staged_calculation.py") -Raw -Encoding UTF8
        foreach ($marker in @("automatic_plan_reuse_disabled", "fresh_search_with_certified_witness", "global_solve_is_explicit")) {
            if (-not $installedStaged.Contains($marker)) {
                throw "Installed P64-L09T-V recalculation marker missing: $marker"
            }
        }
        $installedWitness = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\certified_plan_witness.py") -Raw -Encoding UTF8
        foreach ($marker in @("legacy_rank_policy_migration_required", "search_must_continue", "cache_hit_claimed")) {
            if (-not $installedWitness.Contains($marker)) {
                throw "Installed P64-L09T-V witness marker missing: $marker"
            }
        }
        $installedFinalizer = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\coupled_finalization.py") -Raw -Encoding UTF8
        foreach ($marker in @("bgig.bounded_coupled_finalization.v10", "f_xy_composite_v2_union_cavities_insets", "minimum_reservation_wall_certified")) {
            if (-not $installedFinalizer.Contains($marker)) {
                throw "Installed P64-L09T-V finalizer marker missing: $marker"
            }
        }
        $installedComposite = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\xy_composite_closure.py") -Raw -Encoding UTF8
        foreach ($marker in @("_RESERVATION_DEFERRED_FIRST_OWNER_COUNT", "all_annexes_use_true_vertical_xy_faces", "unions_before_cavities_and_reservation_cuts")) {
            if (-not $installedComposite.Contains($marker)) {
                throw "Installed P64-L09T-V composite marker missing: $marker"
            }
        }
        $installedCad = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\partition_cad.py") -Raw -Encoding UTF8
        foreach ($marker in @("bgig.xy_composite_cad_body.v2", "hybrid_xy_composite_v2", "composite_joins_precede_all_cuts")) {
            if (-not $installedCad.Contains($marker)) {
                throw "Installed P64-L09T-V CAD marker missing: $marker"
            }
        }
        $installedSkeleton = Get-Content -LiteralPath (Join-Path $target "fusion_skeleton.py") -Raw -Encoding UTF8
        foreach ($marker in @("bounded_xy_composite_v1", "hybrid_xy_composite_v2", "_true_vertical_face_axis")) {
            if (-not $installedSkeleton.Contains($marker)) {
                throw "Installed P64-L09T-V Fusion marker missing: $marker"
            }
        }
        $installedPaletteProject = Get-Content -LiteralPath (Join-Path $target "palette_project.py") -Raw -Encoding UTF8
        foreach ($marker in @("legacy_rank_policy_migration_required", "finalized_plan_not_published", "last_attempt")) {
            if (-not $installedPaletteProject.Contains($marker)) {
                throw "Installed P64-L09T-V palette truth marker missing: $marker"
            }
        }

        New-Item -ItemType Directory -Force -Path $projectDirectory | Out-Null
        $utf8NoBom = [Text.UTF8Encoding]::new($false)
        $destinationFixture = Join-Path $projectDirectory $fixtureName
        if (Test-Path -LiteralPath $destinationFixture -PathType Leaf) {
            $existingHash = (Get-FileHash -LiteralPath $destinationFixture -Algorithm SHA256).Hash.ToLowerInvariant()
            $newHash = (Get-FileHash -LiteralPath $tempFixture -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($existingHash -ne $newHash) {
                $backup = Join-Path $projectDirectory "$fixtureName.before-$($existingHash.Substring(0, 12)).json"
                if (-not (Test-Path -LiteralPath $backup -PathType Leaf)) {
                    Copy-Item -LiteralPath $destinationFixture -Destination $backup -Force
                }
            }
        }
        Copy-Item -LiteralPath $tempFixture -Destination $destinationFixture -Force
        Copy-Item -LiteralPath $tempSummary -Destination $summaryPath -Force
        Copy-Item -LiteralPath $tempLocalReceipt -Destination $localReceiptPath -Force

        if (Test-Path -LiteralPath $documentStatePath -PathType Leaf) {
            $stateHash = (Get-FileHash -LiteralPath $documentStatePath -Algorithm SHA256).Hash.ToLowerInvariant()
            $stateBackup = Join-Path $projectDirectory "bgig_document_state_v1.before-p64-l09tv-$($stateHash.Substring(0, 12)).json"
            if (-not (Test-Path -LiteralPath $stateBackup -PathType Leaf)) {
                Copy-Item -LiteralPath $documentStatePath -Destination $stateBackup -Force
            }
        }
        $documentState = [ordered]@{
            schema_version = "bgig.document_state.v1"
            current_path = $destinationFixture
            recent_paths = @($destinationFixture)
            solver_settings = [ordered]@{ method = "auto"; effort = "normal" }
            finishing_effort = "normal"
        } | ConvertTo-Json -Depth 6
        $temporaryState = "$documentStatePath.$PID.tmp"
        [IO.File]::WriteAllText($temporaryState, $documentState + [Environment]::NewLine, $utf8NoBom)
        Move-Item -LiteralPath $temporaryState -Destination $documentStatePath -Force

        [IO.File]::WriteAllText($commitMarker, $commit + [Environment]::NewLine, $utf8NoBom)
        if ((Get-Content -LiteralPath $commitMarker -Raw -Encoding UTF8).Trim() -ne $commit) {
            throw "Installed P64-L09T-V commit marker mismatch."
        }
    }
    catch [UnauthorizedAccessException] {
        Write-Error "Local AppData write blocked. Use Local/Handoff or approve filesystem write."
        exit 21
    }
    catch [IO.IOException] {
        Write-Error "Local AppData write blocked. Use Local/Handoff or approve filesystem write."
        exit 21
    }
    finally {
        if (Test-Path -LiteralPath $workspaceTemp -PathType Container) {
            $resolvedTemp = (Resolve-Path -LiteralPath $workspaceTemp).Path
            $resolvedRoot = (Resolve-Path -LiteralPath $root).Path
            if (-not $resolvedTemp.StartsWith($resolvedRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
                throw "Refusing to remove a P64-L09T-V temp path outside the repository."
            }
            Remove-Item -LiteralPath $resolvedTemp -Recurse -Force
        }
    }
}

Write-Output ""
Write-Output "P64-L09T-V Fusion actions remaining for Thomas:"
Write-Output "1. Fully reload BGIG $expectedVersion and open Atelier de rangement."
Write-Output "2. Open $fixtureName; require Calculer blue, Finaliser orange, Materialiser green, with explicit disabled states."
Write-Output "3. Edit one value; confirm no plan is republished automatically, then click Calculer in Normal."
Write-Output "4. Confirm the tray XY position is automatic and off-center when required, with the minimum wall around every cavity."
Write-Output "5. Finalize and materialize the public fixture; require unions before cuts, frozen cavities and zero printable residual."
Write-Output "6. Open CasLimite01+; calculate and finalize in Normal, then materialize all user containers."
Write-Output "7. Open CasLimite02+; calculate and finalize in Normal, then materialize all user containers."
Write-Output "8. Confirm lower layers are preferred, annexes are welded without internal clearance, and external clearances remain."
Write-Output "9. Trigger or inspect one bounded early stop; require phase, reason, elapsed time, cap and impossibility flag."
Write-Output "10. Report OK or KO with screenshots and scene identity; keep print-validated=false."
Write-Output "Prepared status: fusion-validated=false; print-validated=false."
Write-Output "Prepared P64-L09T-V gate: $(-not $DryRun)"
