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
$preflight = Join-Path $root "scripts\fusion\p64_l09u_r7v_preflight.py"
$localReplay = Join-Path $root "scripts\fusion\p64_l09t_local_replay.py"
$workspaceTemp = Join-Path $root ".codex-work\p64-l09u-r7v-fusion-gate"
$preflightSummary = Join-Path $workspaceTemp "p64-l09u-r7v-preflight-summary.json"
$case02PlusSummary = Join-Path $workspaceTemp "p64-l09u-r7v-case02-plus.json"
$case02PlusPlusSummary = Join-Path $workspaceTemp "p64-l09u-r7v-case02-plus-plus.json"
$commitMarker = Join-Path $target "bgig_installed_commit.txt"

$manifestText = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8
$versionMatch = [regex]::Match(
    $manifestText,
    '"version"\s*:\s*"(?<version>[^\"]+)"'
)
if (-not $versionMatch.Success) {
    throw "Source add-in manifest has no readable version: $manifestPath"
}
$expectedVersion = $versionMatch.Groups["version"].Value
if ($expectedVersion -ne "0.1.78") {
    throw "P64-L09U-R7-V package version mismatch: expected 0.1.78, got $expectedVersion."
}

Write-Output "BGIG P64-L09U-R7-V Fusion gate preparation"
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
        "test_reserved_floor_stack_solver.py",
        "test_p64_l09u_r3_depth_local_insets.py",
        "test_p66_acceptance_prep.py",
        "test_p64_l09u_r7_release_gate.py"
    )) {
        & $python -m unittest discover -s (Join-Path $root "tests") -p $pattern
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    if (-not $DryRun) {
        New-Item -ItemType Directory -Force -Path $workspaceTemp | Out-Null
        & $python $localReplay `
            --case-id case02_plus `
            --write-summary $case02PlusSummary
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & $python $localReplay `
            --case-id case02_plus_plus `
            --write-summary $case02PlusPlusSummary
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & $python $preflight --write-summary $preflightSummary
    }
    else {
        & $python $localReplay --case-id case02_plus
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & $python $localReplay --case-id case02_plus_plus
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
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

if (-not $DryRun) {
    try {
        Assert-BgigPaletteProjectRuntime -AddinPath $target
        & "$PSScriptRoot\check_installed_addin.ps1" `
            -TargetPath $target `
            -ExpectedVersion $expectedVersion
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

        $requiredMarkers = @{
            "fusion_skeleton.py" = @(
                "final_material_envelope_certificate",
                "CAD IR derived geometry is not on the 0.1 mm product grid"
            )
            "lib\board_game_insert_generator\product_grid.py" = @(
                "PRODUCT_GRID_STEP_MM = 0.1",
                "def nearest_ticks"
            )
            "lib\board_game_insert_generator\top_inset_reservation.py" = @(
                "automatic_stack_key_v1",
                "canonical_geometry_digest"
            )
            "lib\board_game_insert_generator\coupled_finalization.py" = @(
                "final_material_envelope_certificate",
                "final_material_fragments_certified"
            )
        }
        foreach ($relativePath in $requiredMarkers.Keys) {
            $installedText = Get-Content -LiteralPath (
                Join-Path $target $relativePath
            ) -Raw -Encoding UTF8
            foreach ($marker in $requiredMarkers[$relativePath]) {
                if (-not $installedText.Contains($marker)) {
                    throw "Installed P64-L09U-R7-V marker missing: $marker"
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
            throw "Installed P64-L09U-R7-V commit marker mismatch."
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
                throw "Refusing to remove an R7 temp path outside the repository."
            }
            Remove-Item -LiteralPath $resolvedTemp -Recurse -Force
        }
    }
}

Write-Output ""
Write-Output "P64-L09U-R7-V actions remaining for Thomas:"
Write-Output "1. Fully close and reopen Fusion, then reload BGIG $expectedVersion."
Write-Output "2. Open CasLimite02+, calculate, finalize and materialize without saving the source."
Write-Output "3. Require at least 1.2 mm of useful material at every box edge, wall and separation."
Write-Output "4. Require useful centered notches, no cut reaching the box edge and no 0.4 mm wall fragment."
Write-Output "5. Open CasLimite02++, calculate, finalize and materialize without saving the source."
Write-Output "6. Require the smaller oriented booklet below and the larger board above wherever they overlap."
Write-Output "7. Require exact local Z steps, no 0.5-0.6 mm micro-notch, no plate and no overhang."
Write-Output "8. Confirm the R6 cavity depths, partial access and direct void continuity remain correct."
Write-Output "9. Compare preview and Fusion scene; record exact times, measurements and screenshots."
Write-Output "10. Follow docs/P64_L09U_R7_V_0178_FUSION_GATE_RECIPE.md."
Write-Output "Prepared status: fusion-validated=false; print-validated=false."
Write-Output "Prepared P64-L09U-R7-V gate: $(-not $DryRun)"
