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
$preflight = Join-Path $root "scripts\fusion\p64_l09rv_preflight.py"
$manifestPath = Join-Path $root "fusion_addin\BoardGameInsertGenerator\BoardGameInsertGenerator.manifest"
$projectDirectory = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "BGIG\projects"
$summaryPath = Join-Path $projectDirectory "p64-l09rv-preflight-summary.json"
$documentStatePath = Join-Path $projectDirectory "bgig_document_state_v1.json"
$commitMarker = Join-Path $target "bgig_installed_commit.txt"
$workspaceTemp = Join-Path $root ".codex-work\p64-l09rv-fusion-gate"
$tempSummary = Join-Path $workspaceTemp "p64-l09rv-preflight-summary.json"
$fixtureNames = @(
    "p64-l09rv-01-preference-envelope.bgig.json",
    "p64-l09rv-02-tray-separated-flow.bgig.json"
)

if (-not (Test-Path -LiteralPath $preflight -PathType Leaf)) {
    throw "P64-L09R-V preflight script missing: $preflight"
}
$manifestText = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8
$versionMatch = [regex]::Match($manifestText, '"version"\s*:\s*"(?<version>[^\"]+)"')
if (-not $versionMatch.Success) {
    throw "Source add-in manifest has no readable version: $manifestPath"
}
$expectedVersion = $versionMatch.Groups["version"].Value
if ($expectedVersion -ne "0.1.65") {
    throw "P64-L09R-V package version mismatch: expected 0.1.65, got $expectedVersion."
}

Write-Output "BGIG P64-L09R-V Fusion gate preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Package version: $expectedVersion"
Write-Output "Target: $target"
Write-Output "Public fixture directory: $projectDirectory"

$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $root "src"
    foreach ($pattern in @(
        "test_minimal_layout_solver.py",
        "test_staged_calculation.py",
        "test_solver_outcome.py",
        "test_scip_product_solver.py",
        "test_fusion_palette_dom.py",
        "test_palette_worker.py",
        "test_p64_l09r_f_representative_hardening.py"
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
    Write-Output "Dry run: would preserve the current document state and any colliding fixture."
    Write-Output "Dry run: would install two public P64-L09R-V fixtures."
    Write-Output "Dry run: would select the tray fixture with calculation Normal and finishing Quick."
    Write-Output "Dry run: would write the exact integrated commit marker."
}
else {
    try {
        Assert-BgigPaletteProjectRuntime -AddinPath $target
        & "$PSScriptRoot\check_installed_addin.ps1" -TargetPath $target -ExpectedVersion $expectedVersion
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

        $installedWorkerPath = Join-Path $target "palette_worker.py"
        $installedWorker = Get-Content -LiteralPath $installedWorkerPath -Raw -Encoding UTF8
        foreach ($marker in @("solve_project", "finalize_project", "source_identity_changed", "worker_pure_data_only")) {
            if (-not $installedWorker.Contains($marker)) {
                throw "Installed P64-L09R-V worker marker missing: $marker"
            }
        }
        if ($installedWorker.Contains("import adsk")) {
            throw "Installed P64-L09R-V worker imports adsk."
        }
        $installedScipSolver = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\scip_product_solver.py") -Raw -Encoding UTF8
        foreach ($marker in @("_invoke_worker_with_top_inset_compensation", "_apply_required_top_inset_z_compensation", "Unexpected SCIP Z expansion")) {
            if (-not $installedScipSolver.Contains($marker)) {
                throw "Installed P64-L09R-V SCIP correction marker missing: $marker"
            }
        }
        $installedScipWorker = Get-Content -LiteralPath (Join-Path $target "vendor\scip\10.0.2\windows-x86_64\worker\scip_real_3d_worker.py") -Raw -Encoding UTF8
        foreach ($marker in @("expandable_z", "expansion_supports", "required_height")) {
            if (-not $installedScipWorker.Contains($marker)) {
                throw "Installed P64-L09R-V SCIP worker marker missing: $marker"
            }
        }        $installedPalette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
        foreach ($marker in @(
            "primary-calculation-action",
            "finalization-action",
            "materialization-action",
            "operation-activity-progress",
            "setInterval(renderOperationActivity,1000)",
            "setInterval(pollAsyncProjectOperations,1000)",
            "3 s max",
            "3 min max",
            "renderSolverSettings();sourceRevision+=1"
        )) {
            if (-not $installedPalette.Contains($marker)) {
                throw "Installed P64-L09R-V palette marker missing: $marker"
            }
        }

        New-Item -ItemType Directory -Force -Path $projectDirectory | Out-Null
        $utf8NoBom = [Text.UTF8Encoding]::new($false)
        foreach ($fixtureName in $fixtureNames) {
            $sourceFixture = Join-Path $workspaceTemp $fixtureName
            $destinationFixture = Join-Path $projectDirectory $fixtureName
            if (Test-Path -LiteralPath $destinationFixture -PathType Leaf) {
                $existingHash = (Get-FileHash -LiteralPath $destinationFixture -Algorithm SHA256).Hash.ToLowerInvariant()
                $newHash = (Get-FileHash -LiteralPath $sourceFixture -Algorithm SHA256).Hash.ToLowerInvariant()
                if ($existingHash -ne $newHash) {
                    $backup = Join-Path $projectDirectory "$fixtureName.before-$($existingHash.Substring(0, 12)).json"
                    if (-not (Test-Path -LiteralPath $backup -PathType Leaf)) {
                        Copy-Item -LiteralPath $destinationFixture -Destination $backup -Force
                    }
                }
            }
            Copy-Item -LiteralPath $sourceFixture -Destination $destinationFixture -Force
        }
        Copy-Item -LiteralPath $tempSummary -Destination $summaryPath -Force

        if (Test-Path -LiteralPath $documentStatePath -PathType Leaf) {
            $stateHash = (Get-FileHash -LiteralPath $documentStatePath -Algorithm SHA256).Hash.ToLowerInvariant()
            $stateBackup = Join-Path $projectDirectory "bgig_document_state_v1.before-p64-l09rv-$($stateHash.Substring(0, 12)).json"
            if (-not (Test-Path -LiteralPath $stateBackup -PathType Leaf)) {
                Copy-Item -LiteralPath $documentStatePath -Destination $stateBackup -Force
            }
        }
        $fixturePaths = @($fixtureNames | ForEach-Object { Join-Path $projectDirectory $_ })
        $trayFixturePath = $fixturePaths[1]
        $documentState = [ordered]@{
            schema_version = "bgig.document_state.v1"
            current_path = $trayFixturePath
            recent_paths = $fixturePaths
            solver_settings = [ordered]@{ method = "auto"; effort = "normal" }
            finishing_effort = "quick"
        } | ConvertTo-Json -Depth 6
        $temporaryState = "$documentStatePath.$PID.tmp"
        [IO.File]::WriteAllText($temporaryState, $documentState + [Environment]::NewLine, $utf8NoBom)
        Move-Item -LiteralPath $temporaryState -Destination $documentStatePath -Force

        [IO.File]::WriteAllText($commitMarker, $commit + [Environment]::NewLine, $utf8NoBom)
        if ((Get-Content -LiteralPath $commitMarker -Raw -Encoding UTF8).Trim() -ne $commit) {
            throw "Installed P64-L09R-V commit marker mismatch."
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
Write-Output "P64-L09R-V Fusion actions remaining for Thomas:"
Write-Output "1. Fully reload BGIG $expectedVersion and open Atelier de rangement."
Write-Output "2. Confirm the activity area is entirely absent at rest and all three product buttons stay visible."
Write-Output "3. Change every calculation budget and confirm its adjacent time updates immediately without touching finishing."
Write-Output "4. Reopen the local 60 / 59.6 / 52.8 mm case with the 1 mm tray, calculate Normal, then materialize the minimal plan without finishing."
Write-Output "5. Open fixture 01, calculate with Normal, and observe the soft small-below-large preference without treating it as a certificate."
Write-Output "6. Open fixture 02, run Quick then Normal calculation, and record elapsed time, displayed budget, result status and engine."
Write-Output "7. Materialize the current minimal plan before any finishing and inspect the tray reservation and cavities."
Write-Output "8. Run Quick finishing separately; confirm the minimal plan remains available if finishing fails."
Write-Output "9. When finishing succeeds, materialize the finalized plan and compare the scene identity."
Write-Output "10. During each operation, observe the full-width activity bar; at rest confirm it leaves no space."
Write-Output "11. Report OK or KO with screenshots and diagnostics; keep print-validated=false."
Write-Output "Prepared P64-L09R-V gate: $(-not $DryRun)"