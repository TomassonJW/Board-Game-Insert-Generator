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
$preflight = Join-Path $root "scripts\fusion\p64_l08k_preflight.py"
$manifestPath = Join-Path $root "fusion_addin\BoardGameInsertGenerator\BoardGameInsertGenerator.manifest"
$projectDirectory = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "BGIG\projects"
$fixturePath = Join-Path $projectDirectory "p64-l08k-real-18x20.bgig.json"
$summaryPath = Join-Path $projectDirectory "p64-l08k-preflight-summary.json"
$documentStatePath = Join-Path $projectDirectory "bgig_document_state_v1.json"
$commitMarker = Join-Path $target "bgig_installed_commit.txt"
$workspaceTemp = Join-Path $root ".codex-work\p64-l08k-fusion-gate"
$tempFixture = Join-Path $workspaceTemp "p64-l08k-real-18x20.bgig.json"
$tempSummary = Join-Path $workspaceTemp "p64-l08k-preflight-summary.json"

if (-not (Test-Path -LiteralPath $preflight -PathType Leaf)) {
    throw "P64-L08K preflight script missing: $preflight"
}
$manifestText = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8
$versionMatch = [regex]::Match($manifestText, '"version"\s*:\s*"(?<version>[^"]+)"')
if (-not $versionMatch.Success) {
    throw "Source add-in manifest has no readable version: $manifestPath"
}
$expectedVersion = $versionMatch.Groups["version"].Value
if ($expectedVersion -ne "0.1.61") {
    throw "P64-L08K package version mismatch: expected 0.1.61, got $expectedVersion."
}

Write-Output "BGIG P64-L08K SCIP product Fusion gate preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Package version: $expectedVersion"
Write-Output "Target: $target"
Write-Output "Reviewed limit fixture: $fixturePath"

$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $root "src"
    foreach ($pattern in @(
        "test_scip_product_solver.py",
        "test_p64_l08k_fusion_preflight.py",
        "test_minimal_layout_solver.py",
        "test_fusion_palette_qt_transport.py"
    )) {
        & $python -m unittest discover -s (Join-Path $root "tests") -p $pattern
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    if ($DryRun) {
        & $python $preflight
    }
    else {
        New-Item -ItemType Directory -Force -Path $workspaceTemp | Out-Null
        & $python $preflight --write-fixture $tempFixture --write-summary $tempSummary
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    $env:PYTHONPATH = $previousPythonPath
}

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($DryRun) {
    Write-Output "Dry run: would preserve the existing document state."
    Write-Output "Dry run: would install the reviewed 18x20 fixture and select Auto intelligent + Approfondi."
    Write-Output "Dry run: would write the installed commit marker."
}
else {
    try {
        Assert-BgigPaletteProjectRuntime -AddinPath $target
        & "$PSScriptRoot\check_installed_addin.ps1" -TargetPath $target -ExpectedVersion $expectedVersion
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

        $installedArtifact = Join-Path $target "vendor\scip\10.0.2\windows-x86_64\ARTIFACT.json"
        $artifact = Get-Content -LiteralPath $installedArtifact -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($artifact.artifact_digest -ne "540e2fe6b9324f2d58afbdaab827760f98b6b0e4ab9f626efdaee69d2c6d2786") {
            throw "Installed P64-L08K SCIP artifact digest mismatch."
        }
        $installedArchive = Join-Path $target "vendor\scip\10.0.2\windows-x86_64\scip-runtime-cp314.zip"
        $archiveHash = (Get-FileHash -LiteralPath $installedArchive -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($archiveHash -ne "0a718ea5884d6326d66777db0ab853a31fa981e6392b89f184342fde27d465c6") {
            throw "Installed P64-L08K SCIP archive digest mismatch."
        }
        $installedSolver = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\minimal_layout_solver.py") -Raw -Encoding UTF8
        foreach ($marker in @(
            "external_scip_real_3d",
            "solve_scip_product_3d",
            "SCIP_STATUS_BOUNDED_UNKNOWN"
        )) {
            if (-not $installedSolver.Contains($marker)) {
                throw "Installed P64-L08K solver marker missing: $marker"
            }
        }

        New-Item -ItemType Directory -Force -Path $projectDirectory | Out-Null
        $utf8NoBom = [Text.UTF8Encoding]::new($false)
        if (Test-Path -LiteralPath $fixturePath -PathType Leaf) {
            $existingHash = (Get-FileHash -LiteralPath $fixturePath -Algorithm SHA256).Hash.ToLowerInvariant()
            $newHash = (Get-FileHash -LiteralPath $tempFixture -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($existingHash -ne $newHash) {
                $backup = Join-Path $projectDirectory "p64-l08k-real-18x20.before-$($existingHash.Substring(0, 12)).bgig.json"
                if (-not (Test-Path -LiteralPath $backup -PathType Leaf)) {
                    Copy-Item -LiteralPath $fixturePath -Destination $backup -Force
                    Write-Output "Existing L08K fixture preserved: $backup"
                }
            }
        }
        Copy-Item -LiteralPath $tempFixture -Destination $fixturePath -Force
        Copy-Item -LiteralPath $tempSummary -Destination $summaryPath -Force

        if (Test-Path -LiteralPath $documentStatePath -PathType Leaf) {
            $stateHash = (Get-FileHash -LiteralPath $documentStatePath -Algorithm SHA256).Hash.ToLowerInvariant()
            $stateBackup = Join-Path $projectDirectory "bgig_document_state_v1.before-p64-l08k-$($stateHash.Substring(0, 12)).json"
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
        $recentPaths = @($fixturePath) + @($recentPaths | Where-Object { $_ -ne $fixturePath })
        $documentState = [ordered]@{
            schema_version = "bgig.document_state.v1"
            current_path = $fixturePath
            recent_paths = @($recentPaths | Select-Object -First 12)
            solver_settings = [ordered]@{ method = "auto"; effort = "deep" }
        } | ConvertTo-Json -Depth 6
        $temporaryState = "$documentStatePath.$PID.tmp"
        [IO.File]::WriteAllText($temporaryState, $documentState + [Environment]::NewLine, $utf8NoBom)
        Move-Item -LiteralPath $temporaryState -Destination $documentStatePath -Force

        [IO.File]::WriteAllText($commitMarker, $commit + [Environment]::NewLine, $utf8NoBom)
        $installedCommit = (Get-Content -LiteralPath $commitMarker -Raw -Encoding UTF8).Trim()
        if ($installedCommit -ne $commit) {
            throw "Installed P64-L08K commit marker mismatch."
        }
        if (-not (Test-Path -LiteralPath $fixturePath -PathType Leaf)) {
            throw "P64-L08K reviewed fixture was not installed."
        }
    }
    catch [UnauthorizedAccessException] {
        Write-Error "P64-L08K local Fusion handoff write blocked: $($_.Exception.Message)"
        exit 21
    }
    catch [IO.IOException] {
        Write-Error "P64-L08K local Fusion handoff write blocked: $($_.Exception.Message)"
        exit 21
    }
    finally {
        if (Test-Path -LiteralPath $workspaceTemp -PathType Container) {
            Remove-Item -LiteralPath $workspaceTemp -Recurse -Force
        }
    }
}

Write-Output ""
Write-Output "P64-L08K Fusion actions remaining:"
Write-Output "1. Recharger l add-in $expectedVersion puis ouvrir la palette BGIG."
Write-Output "2. Verifier que le projet p64-l08k-real-18x20 est charge avec Auto intelligent + Approfondi."
Write-Output "3. Lancer Calculer l agencement une seule fois et attendre au plus 35 secondes."
Write-Output "4. Relever le statut, la source external_scip_real_3d, l invocation SCIP unique et l absence de lanes internes."
Write-Output "5. Tester ensuite ton vrai projet limite de la meme maniere ; materialiser uniquement si BGIG affiche une solution certifiee."
Write-Output "Prepared P64-L08K SCIP product gate: $(-not $DryRun)"