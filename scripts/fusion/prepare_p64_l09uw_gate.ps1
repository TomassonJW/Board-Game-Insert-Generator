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
$preflight = Join-Path $root "scripts\fusion\p64_l09uw_preflight.py"
$localReplay = Join-Path $root "scripts\fusion\p64_l09t_local_replay.py"
$manifestPath = Join-Path $root "fusion_addin\BoardGameInsertGenerator\BoardGameInsertGenerator.manifest"
$projectDirectory = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "BGIG\projects"
$fixtureName = "p64-l09uw-01-exact-composite.bgig.json"
$summaryName = "p64-l09uw-preflight-summary.json"
$localReceiptName = "p64-l09uw-local-replay-summary.json"
$documentStatePath = Join-Path $projectDirectory "bgig_document_state_v1.json"
$commitMarker = Join-Path $target "bgig_installed_commit.txt"
$workspaceTemp = Join-Path $root ".codex-work\p64-l09uw-fusion-gate"
$tempFixture = Join-Path $workspaceTemp $fixtureName
$tempSummary = Join-Path $workspaceTemp $summaryName
$tempLocalReceipt = Join-Path $workspaceTemp $localReceiptName

foreach ($required in @($preflight, $localReplay, $manifestPath)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "P64-L09U-R4-V required source missing: $required"
    }
}
$manifestText = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8
$versionMatch = [regex]::Match(
    $manifestText,
    '"version"\s*:\s*"(?<version>[^\"]+)"'
)
if (-not $versionMatch.Success) {
    throw "Source add-in manifest has no readable version: $manifestPath"
}
$expectedVersion = $versionMatch.Groups["version"].Value
if ($expectedVersion -ne "0.1.75") {
    throw "P64-L09U-R4-V package version mismatch: expected 0.1.75, got $expectedVersion."
}

Write-Output "BGIG P64-L09U-R4-V corrective Fusion gate preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Package version: $expectedVersion"
Write-Output "Target: $target"

$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = ".;$(Join-Path $root 'src')"
    foreach ($pattern in @(
        "test_fusion_materialization_batches.py",
        "test_fusion_palette_project.py",
        "test_fusion_palette_dom.py",
        "test_reserved_floor_stack_solver.py",
        "test_top_inset_reservation.py",
        "test_finalization_stop_diagnostics.py",
        "test_p64_l09t_f_composite_cad.py",
        "test_p64_l09t_g_release_gate.py",
        "test_p64_l09u_corrective_gate.py",
        "test_p64_l09u_r3_depth_local_insets.py"
    )) {
        & $python -m unittest discover -s (Join-Path $root "tests") -p $pattern
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    if (-not $DryRun) {
        New-Item -ItemType Directory -Force -Path $workspaceTemp | Out-Null
        & $python $localReplay --write-summary $tempLocalReceipt
    }
    else {
        & $python $localReplay
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if (-not $DryRun) {
        & $python $preflight `
            --output-directory $workspaceTemp `
            --write-summary $tempSummary
    }
    else {
        & $python $preflight
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    $env:PYTHONPATH = $previousPythonPath
}

& "$PSScriptRoot\install_addin.ps1" `
    -RepoRoot $root `
    -TargetPath $target `
    -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$settings = @{
    action = "inspect"
    input_mode = "quick_parametric_box"
    generation_mode = "compact_only"
    project_root = $root
}
Write-BgigFusionUiSettings `
    -TargetPath $target `
    -Settings $settings `
    -DryRun:$DryRun

if ($DryRun) {
    Write-Output "Dry run: would install the P64-L09U-R4-V fixture and receipts."
    Write-Output "Dry run: would preserve named projects and legacy recovery files."
    Write-Output "Dry run: would force a fresh unsaved startup with no current path."
}
else {
    try {
        Assert-BgigPaletteProjectRuntime -AddinPath $target
        & "$PSScriptRoot\check_installed_addin.ps1" `
            -TargetPath $target `
            -ExpectedVersion $expectedVersion
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

        $installedAdapter = Get-Content -LiteralPath (
            Join-Path $target "BoardGameInsertGenerator.py"
        ) -Raw -Encoding UTF8
        foreach ($marker in @(
            "_create_boolean_rectangular_blank",
            "TemporaryBRepManager.get",
            "BooleanTypes.UnionBooleanType",
            "BooleanTypes.DifferenceBooleanType",
            "_refresh_fusion_generation_ui",
            "_rollback_failed_generation",
            "transient_boolean_module_count",
            "parametric_combine_feature_count"
        )) {
            if (-not $installedAdapter.Contains($marker)) {
                throw "Installed P64-L09U-R4-V materialization marker missing: $marker"
            }
        }
        $installedSkeleton = Get-Content -LiteralPath (
            Join-Path $target "fusion_skeleton.py"
        ) -Raw -Encoding UTF8
        foreach ($marker in @(
            "additive_prism_join_batches",
            "cavity_cut_batches",
            "fusion_materialization_batches",
            "direct_void_to_removable_top_inset",
            "without intermediate material"
        )) {
            if (-not $installedSkeleton.Contains($marker)) {
                throw "Installed P64-L09U-R4-V CAD marker missing: $marker"
            }
        }
        $installedPalette = Get-Content -LiteralPath (
            Join-Path $target "palette_project.py"
        ) -Raw -Encoding UTF8
        foreach ($marker in @(
            "fresh_unsaved_project",
            "cross_session_witness_reuse_disabled",
            "cross_session_witness_persistence_disabled"
        )) {
            if (-not $installedPalette.Contains($marker)) {
                throw "Installed P64-L09U-R4-V startup marker missing: $marker"
            }
        }
        if ($installedPalette.Contains('"autosave_project"')) {
            throw "Installed P64-L09U-R4-V still exposes autosave_project."
        }
        $installedSolver = Get-Content -LiteralPath (
            Join-Path $target "lib\board_game_insert_generator\minimal_layout_solver.py"
        ) -Raw -Encoding UTF8
        foreach ($marker in @(
            "reserved_floor_stack_problem",
            "dense project needs stacks below a tray"
        )) {
            if (-not $installedSolver.Contains($marker)) {
                throw "Installed P64-L09U-R4-V fresh-solve marker missing: $marker"
            }
        }

        New-Item -ItemType Directory -Force -Path $projectDirectory | Out-Null
        $utf8NoBom = [Text.UTF8Encoding]::new($false)
        $destinationFixture = Join-Path $projectDirectory $fixtureName
        Copy-Item -LiteralPath $tempFixture -Destination $destinationFixture -Force
        Copy-Item -LiteralPath $tempSummary -Destination (
            Join-Path $projectDirectory $summaryName
        ) -Force
        Copy-Item -LiteralPath $tempLocalReceipt -Destination (
            Join-Path $projectDirectory $localReceiptName
        ) -Force

        $preservedRecentPaths = @()
        if (Test-Path -LiteralPath $documentStatePath -PathType Leaf) {
            try {
                $previousStateText = Get-Content `
                    -LiteralPath $documentStatePath `
                    -Raw `
                    -Encoding UTF8
                $previousState = ConvertFrom-Json -InputObject $previousStateText
                $preservedRecentPaths = @($previousState.recent_paths)
            }
            catch {
                $preservedRecentPaths = @()
            }
            $stateHash = (
                Get-FileHash -LiteralPath $documentStatePath -Algorithm SHA256
            ).Hash.ToLowerInvariant()
            $stateBackup = Join-Path $projectDirectory (
                "bgig_document_state_v1.before-p64-l09uw-" +
                "$($stateHash.Substring(0, 12)).json"
            )
            if (-not (Test-Path -LiteralPath $stateBackup -PathType Leaf)) {
                Copy-Item `
                    -LiteralPath $documentStatePath `
                    -Destination $stateBackup `
                    -Force
            }
        }
        $recentPaths = New-Object System.Collections.Generic.List[string]
        [void]$recentPaths.Add($destinationFixture)
        foreach ($recentPath in $preservedRecentPaths) {
            $candidatePath = [string]$recentPath
            if (
                $candidatePath `
                -and -not $recentPaths.Contains($candidatePath)
            ) {
                [void]$recentPaths.Add($candidatePath)
            }
        }
        $documentState = [ordered]@{
            schema_version = "bgig.document_state.v1"
            current_path = ""
            recent_paths = @($recentPaths)
            solver_settings = [ordered]@{
                method = "auto"
                effort = "normal"
            }
            finishing_effort = "normal"
        } | ConvertTo-Json -Depth 6
        $temporaryState = "$documentStatePath.$PID.tmp"
        [IO.File]::WriteAllText(
            $temporaryState,
            $documentState + [Environment]::NewLine,
            $utf8NoBom
        )
        Move-Item `
            -LiteralPath $temporaryState `
            -Destination $documentStatePath `
            -Force

        [IO.File]::WriteAllText(
            $commitMarker,
            $commit + [Environment]::NewLine,
            $utf8NoBom
        )
        $installedCommit = (
            Get-Content -LiteralPath $commitMarker -Raw -Encoding UTF8
        ).Trim()
        if ($installedCommit -ne $commit) {
            throw "Installed P64-L09U-R4-V commit marker mismatch."
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
            if (-not $resolvedTemp.StartsWith(
                $resolvedRoot + [IO.Path]::DirectorySeparatorChar,
                [StringComparison]::OrdinalIgnoreCase
            )) {
                throw "Refusing to remove a P64-L09U-R4-V temp path outside the repository."
            }
            Remove-Item -LiteralPath $resolvedTemp -Recurse -Force
        }
    }
}

Write-Output ""
Write-Output "P64-L09U-R4-V actions remaining for Thomas:"
Write-Output "1. Fully close and reopen Fusion, then reload BGIG $expectedVersion."
Write-Output "2. Confirm BGIG opens on a fresh unsaved empty project."
Write-Output "3. Open CasLimite01+, calculate and finalize in Normal; remove the tray and require every covered cavity to be directly open, with no intermediate wall."
Write-Output "4. Require separate search, cap, termination and total wall times; never an unexplained 24 s / 20 s max."
Write-Output "5. Materialize and require no ALL_TOOL_BODY_REFERENCE_LOST, no Combine feature and no partial scene."
Write-Output "6. Repeat CasLimite01+ without its flat item, without saving; require top-open calibrated cavities."
Write-Output "7. Open CasLimite02+; require every covered cavity to remain accessible under the two exact local tray footprints and steps."
Write-Output "8. Open CasLimite01++, then calculate, finalize and materialize it without saving the source."
Write-Output "9. Require synchronized preview/Fusion geometry, progressive modules and unchanged calibrated depths."
Write-Output "10. Follow docs/P64_L09U_R4_V_0175_FUSION_GATE_RECIPE.md and report exact times, measurements and screenshots."
Write-Output "Prepared status: fusion-validated=false; print-validated=false."
Write-Output "Prepared P64-L09U-R4-V gate: $(-not $DryRun)"
