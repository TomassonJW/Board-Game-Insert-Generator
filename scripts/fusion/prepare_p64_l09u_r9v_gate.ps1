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
$manifestPath = Join-Path $root "fusion_addin\BoardGameInsertGenerator\BoardGameInsertGenerator.manifest"
$preflight = Join-Path $root "scripts\fusion\p64_l09u_r9v_preflight.py"
$localReplay = Join-Path $root "scripts\fusion\p64_l09t_local_replay.py"
$workspaceTemp = Join-Path $root ".codex-work\p64-l09u-r9v-fusion-gate"
$preflightSummary = Join-Path $workspaceTemp "p64-l09u-r9v-preflight-summary.json"
$case02PlusSummary = Join-Path $workspaceTemp "p64-l09u-r9v-case02-plus.json"
$case02PlusPlusSummary = Join-Path $workspaceTemp "p64-l09u-r9v-case02-plus-plus.json"
$commitMarker = Join-Path $target "bgig_installed_commit.txt"
$authoritativePlacementDigest = "a3ef2f440a212ed29496fe50072e065a0c861388e6e55e68c548c2bf8817bc46"

$manifestText = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8
$versionMatch = [regex]::Match(
    $manifestText,
    '"version"\s*:\s*"(?<version>[^\"]+)"'
)
if (-not $versionMatch.Success) {
    throw "Source add-in manifest has no readable version: $manifestPath"
}
$expectedVersion = $versionMatch.Groups["version"].Value
if ($expectedVersion -ne "0.1.80") {
    throw "P64-L09U-R9-V package version mismatch: expected 0.1.80, got $expectedVersion."
}

function Assert-R9ReplayReceipt {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path,
        [Parameter(Mandatory = $true)]
        [string] $CaseId,
        [Parameter(Mandatory = $true)]
        [string] $ExpectedSha256
    )

    $receipt = Get-Content -LiteralPath $Path -Raw -Encoding UTF8 |
        ConvertFrom-Json
    if (
        $receipt.status -ne "passed" -or
        $receipt.read_only -ne $true -or
        $receipt.repository_payload_written -ne $false -or
        $receipt.calculation_effort -ne "deep" -or
        $receipt.case_count -ne 1
    ) {
        throw "R9 replay contract failed for $CaseId."
    }
    $before = $receipt.source_sha256_before.$CaseId
    $after = $receipt.source_sha256_after.$CaseId
    if (
        $before -ne $ExpectedSha256 -or
        $after -ne $ExpectedSha256
    ) {
        throw "R9 personal project digest changed for $CaseId."
    }
    $result = $receipt.results[0]
    $strict = $result.strict_flat_inset_certificate
    if (
        $result.case_id -ne $CaseId -or
        $result.calculation_effort -ne "deep" -or
        $result.placement_digest -ne $authoritativePlacementDigest -or
        $result.calculation_status -ne "solution_found" -or
        $result.finalization_status -ne "solution_found" -or
        $result.cad_status -ne "ready_for_fusion" -or
        $result.cavities_frozen -ne $true -or
        $result.calibrated_cavity_depths_unchanged -ne $true -or
        $result.top_void_continuity_certified -ne $true -or
        $strict.certified -ne $true -or
        $strict.positive_geometry_unchanged -ne $true -or
        $strict.flat_positive_volume_mm3 -ne 0 -or
        $strict.flat_positive_body_count -ne 0 -or
        $strict.flat_positive_union_count -ne 0 -or
        $strict.new_printable_body_count_attributed_to_flat_items -ne 0
    ) {
        throw "R9 functional authority diverged for $CaseId."
    }
    Write-Output (
        (
            "R9_REPLAY case={0} calculation_ms={1} finalization_ms={2} " +
            "placement={3} sha_unchanged=true"
        ) -f @(
            $CaseId,
            $result.calculation_observed_ms,
            $result.finishing_observed_ms,
            $result.placement_digest
        )
    )
}

Write-Output "BGIG P64-L09U-R9-V Fusion gate preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Package version: $expectedVersion"
Write-Output "Target: $target"

$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = "$(Join-Path $root 'src');$root"
    foreach ($pattern in @(
        "test_product_grid.py",
        "test_flat_stack_reservation.py",
        "test_top_inset_reservation.py",
        "test_minimal_layout_solver.py",
        "test_staged_calculation.py",
        "test_scip_product_solver.py",
        "test_certified_plan_witness.py",
        "test_p64_l09u_r8_subtractive_flat_insets.py",
        "test_p64_l09t_f_composite_cad.py",
        "test_partition_result_view.py",
        "test_fusion_palette_dom.py",
        "test_p66_acceptance_prep.py",
        "test_p64_l09u_r9_release_gate.py"
    )) {
        & $python -m unittest discover -s (Join-Path $root "tests") -p $pattern
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }

    New-Item -ItemType Directory -Force -Path $workspaceTemp |
        Out-Null
    & $python $localReplay `
        --case-id case02_plus `
        --calculation-effort deep `
        --include-diagnostics `
        --write-summary $case02PlusSummary
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $python $localReplay `
        --case-id case02_plus_plus `
        --calculation-effort deep `
        --include-diagnostics `
        --write-summary $case02PlusPlusSummary
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $python $preflight --write-summary $preflightSummary
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Assert-R9ReplayReceipt `
        -Path $case02PlusSummary `
        -CaseId "case02_plus" `
        -ExpectedSha256 "5e84fe6f5c0b3e5f046201d442c414504dd95d4db8e711169a2624485466d7dc"
    Assert-R9ReplayReceipt `
        -Path $case02PlusPlusSummary `
        -CaseId "case02_plus_plus" `
        -ExpectedSha256 "83e9e90a6bfd86b18d3a157077a0e63dc2f543ddab626adb2151e269e01d9743"
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

if (-not $DryRun) {
    try {
        Assert-BgigPaletteProjectRuntime -AddinPath $target
        & "$PSScriptRoot\check_installed_addin.ps1" `
            -TargetPath $target `
            -ExpectedVersion $expectedVersion
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

        $requiredMarkers = @{
            "fusion_skeleton.py" = @(
                "subtractive_flat_inset_certificate",
                "strictly_subtractive_flat_inset_v1"
            )
            "BoardGameInsertGenerator.py" = @(
                "Fusion transient cuts accept difference operations only.",
                "Fusion flat-inset BRep tool diverges from its exact interval."
            )
            "lib\board_game_insert_generator\minimal_layout_solver.py" = @(
                "p64-l09u-r9-c-v2",
                "_uses_r9_certified_internal_prefix",
                "first_certified_geometric_group_authority"
            )
            "lib\board_game_insert_generator\top_inset_reservation.py" = @(
                "automatic_rank_cache_hit_count",
                "_placement_material_rectangles",
                "_reserved_prism_placement_bounds"
            )
            "lib\board_game_insert_generator\flat_inset_subtraction.py" = @(
                "bgig.flat_inset_subtraction_plan.v1",
                "bgig.subtractive_flat_inset_certificate.v1"
            )
            "lib\board_game_insert_generator\coupled_finalization.py" = @(
                "finalized_container_geometry_certificate",
                "flat_inset_subtraction_plan"
            )
        }
        foreach ($relativePath in $requiredMarkers.Keys) {
            $installedText = Get-Content -LiteralPath (
                Join-Path $target $relativePath
            ) -Raw -Encoding UTF8
            foreach ($marker in $requiredMarkers[$relativePath]) {
                if (-not $installedText.Contains($marker)) {
                    throw "Installed P64-L09U-R9-V marker missing: $marker"
                }
            }
        }

        $utf8NoBom = [Text.UTF8Encoding]::new($false)
        [IO.File]::WriteAllText(
            $commitMarker,
            $commit + [Environment]::NewLine,
            $utf8NoBom
        )
        $installedCommit = (
            Get-Content -LiteralPath $commitMarker -Raw -Encoding UTF8
        ).Trim()
        if ($installedCommit -ne $commit) {
            throw "Installed P64-L09U-R9-V commit marker mismatch."
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
}

if (Test-Path -LiteralPath $workspaceTemp -PathType Container) {
    $resolvedTemp = (Resolve-Path -LiteralPath $workspaceTemp).Path
    $resolvedRoot = (Resolve-Path -LiteralPath $root).Path
    if (-not $resolvedTemp.StartsWith(
        $resolvedRoot + [IO.Path]::DirectorySeparatorChar,
        [StringComparison]::OrdinalIgnoreCase
    )) {
        throw "Refusing to remove an R9 temp path outside the repository."
    }
    Remove-Item -LiteralPath $resolvedTemp -Recurse -Force
}

Write-Output ""
Write-Output "P64-L09U-R9-V actions remaining for Thomas:"
Write-Output "1. Fully close and reopen Fusion, then reload BGIG $expectedVersion."
Write-Output "2. Use Deep calculation on CasLimite02+ without saving the source."
Write-Output "3. Record calculation, finalization and materialization times."
Write-Output "4. Confirm the already accepted geometry, order and layout at a glance."
Write-Output "5. Repeat only this R9 performance gate on CasLimite02++."
Write-Output "6. Follow docs/P64_L09U_R9_V_0180_FUSION_GATE_RECIPE.md."
Write-Output "Prepared status: fusion-validated=false; print-validated=false."
Write-Output "Prepared P64-L09U-R9-V gate: $(-not $DryRun)"
