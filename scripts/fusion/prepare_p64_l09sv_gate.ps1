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
$preflight = Join-Path $root "scripts\fusion\p64_l09sv_preflight.py"
$manifestPath = Join-Path $root "fusion_addin\BoardGameInsertGenerator\BoardGameInsertGenerator.manifest"
$projectDirectory = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "BGIG\projects"
$fixtureName = "p64-l09sv-01-recent-tray-composite.bgig.json"
$summaryPath = Join-Path $projectDirectory "p64-l09sv-preflight-summary.json"
$documentStatePath = Join-Path $projectDirectory "bgig_document_state_v1.json"
$commitMarker = Join-Path $target "bgig_installed_commit.txt"
$workspaceTemp = Join-Path $root ".codex-work\p64-l09sv-fusion-gate"
$tempSummary = Join-Path $workspaceTemp "p64-l09sv-preflight-summary.json"
$tempFixture = Join-Path $workspaceTemp $fixtureName

if (-not (Test-Path -LiteralPath $preflight -PathType Leaf)) {
    throw "P64-L09S-V preflight script missing: $preflight"
}
$manifestText = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8
$versionMatch = [regex]::Match($manifestText, '"version"\s*:\s*"(?<version>[^\"]+)"')
if (-not $versionMatch.Success) {
    throw "Source add-in manifest has no readable version: $manifestPath"
}
$expectedVersion = $versionMatch.Groups["version"].Value
if ($expectedVersion -ne "0.1.68") {
    throw "P64-L09S-V package version mismatch: expected 0.1.68, got $expectedVersion."
}

Write-Output "BGIG P64-L09S-V Fusion gate preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Package version: $expectedVersion"
Write-Output "Target: $target"
Write-Output "Fixture directory: $projectDirectory"

$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = ".;$(Join-Path $root 'src')"
    foreach ($pattern in @(
        "test_floor_maxrects_solver.py",
        "test_top_inset_reservation.py",
        "test_xy_composite_closure.py",
        "test_composite_fusion_contract.py",
        "test_staged_calculation.py",
        "test_partition_cad.py",
        "test_fusion_palette_project.py",
        "test_p64_l09s_f_end_to_end_hardening.py"
    )) {
        & $python -m unittest discover -s (Join-Path $root "tests") -p $pattern
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    if ($DryRun) {
        & $python $preflight
    }
    else {
        New-Item -ItemType Directory -Force -Path $workspaceTemp | Out-Null
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
    Write-Output "Dry run: would install the P64-L09S-V fixture and preflight receipt."
    Write-Output "Dry run: would preserve any existing document state and colliding fixture."
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
                throw "Installed P64-L09S-V worker marker missing: $marker"
            }
        }
        if ($installedWorker.Contains("import adsk")) {
            throw "Installed P64-L09S-V worker imports adsk."
        }

        $installedMinimalSolver = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\minimal_layout_solver.py") -Raw -Encoding UTF8
        foreach ($marker in @("p64-l09s-v2", "finishing_candidate_pool", "_merge_projected_finishing_candidates")) {
            if (-not $installedMinimalSolver.Contains($marker)) {
                throw "Installed P64-L09S-V minimal solver marker missing: $marker"
            }
        }

        $installedFinalizer = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\coupled_finalization.py") -Raw -Encoding UTF8
        foreach ($marker in @("bgig.bounded_coupled_finalization.v8", "_resolve_frontiers", "minimal_candidate_selection", "e_xy_composite_union_and_exact_insets", "xy_composite_cad_materialization_certified")) {
            if (-not $installedFinalizer.Contains($marker)) {
                throw "Installed P64-L09S-V finalizer marker missing: $marker"
            }
        }
        $installedComposite = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\xy_composite_closure.py") -Raw -Encoding UTF8
        foreach ($marker in @("Bounded XY-composite", "all_annexes_use_true_vertical_xy_faces", "edge_or_point_attachment_count")) {
            if (-not $installedComposite.Contains($marker)) {
                throw "Installed P64-L09S-V composite marker missing: $marker"
            }
        }
        $installedCad = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\partition_cad.py") -Raw -Encoding UTF8
        foreach ($marker in @("bgig.xy_composite_cad_body.v1", "composite_rectangular_union", "join_rectangular_prism", "composite_joins_precede_all_cuts")) {
            if (-not $installedCad.Contains($marker)) {
                throw "Installed P64-L09S-V CAD marker missing: $marker"
            }
        }
        $installedSkeleton = Get-Content -LiteralPath (Join-Path $target "fusion_skeleton.py") -Raw -Encoding UTF8
        foreach ($marker in @("bounded_xy_composite_v1", "_true_vertical_face_axis", "composite_rectangular_union")) {
            if (-not $installedSkeleton.Contains($marker)) {
                throw "Installed P64-L09S-V Fusion plan marker missing: $marker"
            }
        }
        $installedPalette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
        foreach ($marker in @("#1769aa", "#b85f14", "#237a4b")) {
            if (-not $installedPalette.Contains($marker)) {
                throw "Installed P64-L09S-V palette marker missing: $marker"
            }
        }

        $installedPaletteProject = Get-Content -LiteralPath (Join-Path $target "palette_project.py") -Raw -Encoding UTF8
        foreach ($marker in @("finalized_plan_ready", "finalized_plan_not_published", "materializable", "last_attempt")) {
            if (-not $installedPaletteProject.Contains($marker)) {
                throw "Installed P64-L09S-V palette truth marker missing: $marker"
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

        if (Test-Path -LiteralPath $documentStatePath -PathType Leaf) {
            $stateHash = (Get-FileHash -LiteralPath $documentStatePath -Algorithm SHA256).Hash.ToLowerInvariant()
            $stateBackup = Join-Path $projectDirectory "bgig_document_state_v1.before-p64-l09sv-$($stateHash.Substring(0, 12)).json"
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
            throw "Installed P64-L09S-V commit marker mismatch."
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
            Remove-Item -LiteralPath $workspaceTemp -Recurse -Force
        }
    }
}

Write-Output ""
Write-Output "P64-L09S-V Fusion actions remaining for Thomas:"
Write-Output "1. Fully reload BGIG $expectedVersion and open Atelier de rangement."
Write-Output "2. Confirm Calculer is blue, Finaliser orange, Materialiser green, with explicit disabled states."
Write-Output "3. Open $fixtureName and complete the public Normal calculation/finalization/materialization smoke with zero printable residual."
Write-Output "4. Open CasLimite01; with one tray, then with several trays, calculate in Approfondi and require a certified solution from the SCIP lane."
Write-Output "5. On CasLimite01, verify every source minimum and fixed axis, no artificial tray-support growth, then finalize and materialize without false success."
Write-Output "6. Open CasLimite02 with its two trays, calculate, then finalize under the visible shared budget; require a current finalized plan and zero printable residual."
Write-Output "7. On CasLimite02, verify the bounded candidate selection, c2 fixed X, every minimum envelope, welded XY annexes, exact notches and one user component per owner."
Write-Output "8. Report OK or KO for each case with screenshots, scene identity and diagnostics; keep print-validated=false."
Write-Output "Prepared P64-L09S-V gate: $(-not $DryRun)"
