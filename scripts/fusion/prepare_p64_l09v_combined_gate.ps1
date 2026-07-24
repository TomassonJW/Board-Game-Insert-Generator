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
$preflight = Join-Path $root "scripts\fusion\p64_l09v_preflight.py"
$manifestPath = Join-Path $root "fusion_addin\BoardGameInsertGenerator\BoardGameInsertGenerator.manifest"
$projectDirectory = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "BGIG\projects"
$summaryPath = Join-Path $projectDirectory "p64-l09v-preflight-summary.json"
$documentStatePath = Join-Path $projectDirectory "bgig_document_state_v1.json"
$commitMarker = Join-Path $target "bgig_installed_commit.txt"
$workspaceTemp = Join-Path $root ".codex-work\p64-l09v-fusion-gate"
$tempSummary = Join-Path $workspaceTemp "p64-l09v-preflight-summary.json"
$fixtureNames = @(
    "p64-l09v-01-anti-fall-negative.bgig.json",
    "p64-l09v-02-stable-bridge.bgig.json",
    "p64-l09v-03-tray-finalization.bgig.json"
)

if (-not (Test-Path -LiteralPath $preflight -PathType Leaf)) {
    throw "P64-L09V preflight script missing: $preflight"
}
$manifestText = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8
$versionMatch = [regex]::Match($manifestText, '"version"\s*:\s*"(?<version>[^"]+)"')
if (-not $versionMatch.Success) {
    throw "Source add-in manifest has no readable version: $manifestPath"
}
$expectedVersion = $versionMatch.Groups["version"].Value
if ($expectedVersion -ne "0.1.63") {
    throw "P64-L09V package version mismatch: expected 0.1.63, got $expectedVersion."
}

Write-Output "BGIG P64-L09V combined Fusion gate preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Package version: $expectedVersion"
Write-Output "Target: $target"
Write-Output "Public fixture directory: $projectDirectory"

$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $root "src"
    foreach ($pattern in @(
        "test_material_support.py",
        "test_scip_product_solver.py",
        "test_free_3d_continuous_closure.py",
        "test_staged_calculation.py",
        "test_fusion_palette_project.py",
        "test_p64_l09v_fusion_preflight.py"
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
    Write-Output "Dry run: would preserve the existing document state."
    Write-Output "Dry run: would install three public L09V fixtures."
    Write-Output "Dry run: would select the tray fixture with Auto intelligent + Approfondi."
    Write-Output "Dry run: would write the installed commit marker."
}
else {
    try {
        Assert-BgigPaletteProjectRuntime -AddinPath $target
        & "$PSScriptRoot\check_installed_addin.ps1" -TargetPath $target -ExpectedVersion $expectedVersion
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

        $preflightSummary = Get-Content -LiteralPath $tempSummary -Raw -Encoding UTF8 | ConvertFrom-Json
        $installedArtifact = Join-Path $target "vendor\scip\10.0.2\windows-x86_64\ARTIFACT.json"
        $artifact = Get-Content -LiteralPath $installedArtifact -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($artifact.artifact_digest -ne $preflightSummary.scip_runtime_artifact_digest) {
            throw "Installed P64-L09V SCIP artifact digest mismatch."
        }
        $installedArchive = Join-Path $target "vendor\scip\10.0.2\windows-x86_64\scip-runtime-cp314.zip"
        $archiveHash = (Get-FileHash -LiteralPath $installedArchive -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($archiveHash -ne $preflightSummary.scip_runtime_archive_sha256) {
            throw "Installed P64-L09V SCIP archive digest mismatch."
        }

        $installedMaterialSupport = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\material_support.py") -Raw -Encoding UTF8
        foreach ($marker in @("material_surface_v1", "falls_through_opening", "uncertified_lid_ignored")) {
            if (-not $installedMaterialSupport.Contains($marker)) {
                throw "Installed P64-L09V material support marker missing: $marker"
            }
        }
        $installedProductSolver = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\scip_product_solver.py") -Raw -Encoding UTF8
        foreach ($marker in @("top_inset_support", "top_inset_support_profiles")) {
            if (-not $installedProductSolver.Contains($marker)) {
                throw "Installed P64-L09V SCIP top inset marker missing: $marker"
            }
        }
        if ($installedProductSolver.Contains('return None, "top_inset_reservations_not_supported"')) {
            throw "Installed P64-L09V SCIP product solver still rejects all top inset reservations."
        }
        $installedFinalizer = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\coupled_finalization.py") -Raw -Encoding UTF8
        foreach ($marker in @(
            "bounded_growth_local_repair_balanced_proportional",
            "bgig.finalization_secondary_objectives.v1",
            "f01b_certified_baseline"
        )) {
            if (-not $installedFinalizer.Contains($marker)) {
                throw "Installed P64-L09V finalization marker missing: $marker"
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
                    $stem = [IO.Path]::GetFileNameWithoutExtension($fixtureName)
                    $backup = Join-Path $projectDirectory "$stem.before-$($existingHash.Substring(0, 12)).json"
                    if (-not (Test-Path -LiteralPath $backup -PathType Leaf)) {
                        Copy-Item -LiteralPath $destinationFixture -Destination $backup -Force
                        Write-Output "Existing L09V fixture preserved: $backup"
                    }
                }
            }
            Copy-Item -LiteralPath $sourceFixture -Destination $destinationFixture -Force
        }
        Copy-Item -LiteralPath $tempSummary -Destination $summaryPath -Force

        if (Test-Path -LiteralPath $documentStatePath -PathType Leaf) {
            $stateHash = (Get-FileHash -LiteralPath $documentStatePath -Algorithm SHA256).Hash.ToLowerInvariant()
            $stateBackup = Join-Path $projectDirectory "bgig_document_state_v1.before-p64-l09v-$($stateHash.Substring(0, 12)).json"
            if (-not (Test-Path -LiteralPath $stateBackup -PathType Leaf)) {
                Copy-Item -LiteralPath $documentStatePath -Destination $stateBackup -Force
                Write-Output "Document state preserved: $stateBackup"
            }
        }
        $recentPaths = @()
        if (Test-Path -LiteralPath $documentStatePath -PathType Leaf) {
            try {
                $previousState = Get-Content -LiteralPath $documentStatePath -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($previousState.schema_version -eq "bgig.document_state.v1") {
                    $recentPaths = @($previousState.recent_paths | Where-Object { $_ -is [string] })
                }
            }
            catch {
                $recentPaths = @()
            }
        }
        $fixturePaths = @($fixtureNames | ForEach-Object { Join-Path $projectDirectory $_ })
        $recentPaths = @($fixturePaths) + @($recentPaths | Where-Object { $fixturePaths -notcontains $_ })
        $trayFixturePath = Join-Path $projectDirectory $fixtureNames[2]
        $documentState = [ordered]@{
            schema_version = "bgig.document_state.v1"
            current_path = $trayFixturePath
            recent_paths = @($recentPaths | Select-Object -First 12)
            solver_settings = [ordered]@{ method = "auto"; effort = "deep" }
        } | ConvertTo-Json -Depth 6
        $temporaryState = "$documentStatePath.$PID.tmp"
        [IO.File]::WriteAllText($temporaryState, $documentState + [Environment]::NewLine, $utf8NoBom)
        Move-Item -LiteralPath $temporaryState -Destination $documentStatePath -Force

        [IO.File]::WriteAllText($commitMarker, $commit + [Environment]::NewLine, $utf8NoBom)
        $installedCommit = (Get-Content -LiteralPath $commitMarker -Raw -Encoding UTF8).Trim()
        if ($installedCommit -ne $commit) {
            throw "Installed P64-L09V commit marker mismatch."
        }
        foreach ($fixtureName in $fixtureNames) {
            if (-not (Test-Path -LiteralPath (Join-Path $projectDirectory $fixtureName) -PathType Leaf)) {
                throw "P64-L09V public fixture was not installed: $fixtureName"
            }
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
Write-Output "P64-L09V Fusion actions remaining:"
Write-Output "1. Recharger l add-in $expectedVersion puis ouvrir la palette BGIG."
Write-Output "2. Garder Auto intelligent + Approfondi."
Write-Output "3. Ouvrir 01 anti-chute, calculer une fois et verifier qu aucun petit bac n est certifie au-dessus d une ouverture qui peut l avaler."
Write-Output "4. Ouvrir 02 pontage stable, calculer puis verifier qu un appui materiel stable reste admis."
Write-Output "5. Ouvrir 03 plateau et fermeture, calculer puis finaliser ; verifier SCIP, encastrement Z, cavites intactes et volume final."
Write-Output "6. Ne materialiser que le plan final certifie ; relever statut, moteur, temps et diagnostic."
Write-Output "7. Confirmer que has_lid seul ne cree ni surface pleine ni nouvelle pose et que print-validated=false."
Write-Output "Prepared P64-L09V combined gate: $(-not $DryRun)"
