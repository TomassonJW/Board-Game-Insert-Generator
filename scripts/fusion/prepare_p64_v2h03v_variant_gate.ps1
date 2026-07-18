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
$variantFixture = Join-Path $root "scripts\fusion\p64_v2h03v_variant_project.json"
$controlFixture = Join-Path $root "scripts\fusion\p64_v2h03v_simple_control_project.json"
$preflightScript = Join-Path $root "scripts\fusion\p64_v2h03v_preflight.py"
$projectDirectory = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "BGIG\projects"
$currentProjectPath = Join-Path $projectDirectory "bgig_project_v1.json"
$projectBackupPath = Join-Path $projectDirectory "bgig_project_v1.before-p64-v2h03v.json"
$variantDocumentPath = Join-Path $projectDirectory "p64-v2h03v-variant-dead-end.bgig.json"
$controlDocumentPath = Join-Path $projectDirectory "p64-v2h03v-simple-control.bgig.json"
$documentStatePath = Join-Path $projectDirectory "bgig_document_state_v1.json"
$documentStateBackupPath = Join-Path $projectDirectory "bgig_document_state_v1.before-p64-v2h03v.json"
$commitMarker = Join-Path $target "bgig_installed_commit.txt"

foreach ($required in @($variantFixture, $controlFixture, $preflightScript)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "P64-V2H03V required artifact missing: $required"
    }
}

Write-Output "BGIG P64-V2H03V internal-variant Fusion gate preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"
Write-Output "Variant fixture: $variantFixture"
Write-Output "Canonical control: $controlFixture"

$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $root "src"
    & $python -m unittest discover -s (Join-Path $root "tests") -p "test_p64_v2h03v_fusion_gate.py"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $python $preflightScript $variantFixture $controlFixture
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    $env:PYTHONPATH = $previousPythonPath
}

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.55"') {
        throw "Installed P64-V2H03V package mismatch: expected 0.1.55."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        "function containerVariantTraceDetails",
        "container-variant-diagnostics",
        "trace.canonical_portfolio_completed_first",
        "trace.cartesian_product_materialized",
        "counters.variant_assignment_states",
        "counters.variant_placement_trials"
    )) {
        if (-not $palette.Contains($marker)) {
            throw "Installed P64-V2H03V palette marker missing: $marker"
        }
    }
    $variantSearch = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\container_variant_global_search.py") -Raw -Encoding UTF8
    foreach ($marker in @("container_variant_global_execution_to_dict", "canonical_portfolio_completed_first", "cartesian_product_materialized")) {
        if (-not $variantSearch.Contains($marker)) {
            throw "Installed P64-V2H03V variant-search marker missing: $marker"
        }
    }
    $localVariants = Join-Path $target "lib\board_game_insert_generator\container_internal_variants.py"
    if (-not (Test-Path -LiteralPath $localVariants -PathType Leaf)) {
        throw "Installed P64-V2H03V local-variant runtime missing: $localVariants"
    }
}

if ($DryRun) {
    Write-Output "Dry run: would preserve a different current project at $projectBackupPath"
    Write-Output "Dry run: would install the variant fixture at $currentProjectPath and $variantDocumentPath"
    Write-Output "Dry run: would install the canonical control at $controlDocumentPath"
    Write-Output "Dry run: would set palette solver_settings to auto + quick in $documentStatePath"
    Write-Output "Dry run: would write installed commit marker at $commitMarker"
}
else {
    try {
        New-Item -ItemType Directory -Force -Path $projectDirectory | Out-Null
        $variantHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $variantFixture).Hash
        if (Test-Path -LiteralPath $currentProjectPath -PathType Leaf) {
            $currentHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $currentProjectPath).Hash
            if ($currentHash -ne $variantHash) {
                $resolvedProjectBackup = $projectBackupPath
                if (Test-Path -LiteralPath $resolvedProjectBackup -PathType Leaf) {
                    $shortCurrentHash = $currentHash.Substring(0, 12).ToLowerInvariant()
                    $resolvedProjectBackup = Join-Path $projectDirectory "bgig_project_v1.before-p64-v2h03v-$shortCurrentHash.json"
                }
                if (-not (Test-Path -LiteralPath $resolvedProjectBackup -PathType Leaf)) {
                    Copy-Item -LiteralPath $currentProjectPath -Destination $resolvedProjectBackup -Force
                    Write-Output "Current project preserved: $resolvedProjectBackup"
                }
                else {
                    Write-Output "Matching P64-V2H03V project backup preserved: $resolvedProjectBackup"
                }
            }
        }
        foreach ($copy in @(
            @($variantFixture, $currentProjectPath),
            @($variantFixture, $variantDocumentPath),
            @($controlFixture, $controlDocumentPath)
        )) {
            $temporary = "$($copy[1]).$PID.tmp"
            Copy-Item -LiteralPath $copy[0] -Destination $temporary -Force
            Move-Item -LiteralPath $temporary -Destination $copy[1] -Force
        }

        if (Test-Path -LiteralPath $documentStatePath -PathType Leaf) {
            $resolvedStateBackup = $documentStateBackupPath
            if (Test-Path -LiteralPath $resolvedStateBackup -PathType Leaf) {
                $stateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $documentStatePath).Hash.Substring(0, 12).ToLowerInvariant()
                $resolvedStateBackup = Join-Path $projectDirectory "bgig_document_state_v1.before-p64-v2h03v-$stateHash.json"
            }
            if (-not (Test-Path -LiteralPath $resolvedStateBackup -PathType Leaf)) {
                Copy-Item -LiteralPath $documentStatePath -Destination $resolvedStateBackup -Force
                Write-Output "Document state preserved: $resolvedStateBackup"
            }
            else {
                Write-Output "Matching P64-V2H03V document-state backup preserved: $resolvedStateBackup"
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
        $recentPaths = @($variantDocumentPath, $controlDocumentPath) + @($recentPaths | Where-Object { $_ -notin @($variantDocumentPath, $controlDocumentPath) })
        $documentState = [ordered]@{
            schema_version = "bgig.document_state.v1"
            current_path = $variantDocumentPath
            recent_paths = @($recentPaths | Select-Object -First 12)
            solver_settings = [ordered]@{ method = "auto"; effort = "quick" }
        } | ConvertTo-Json -Depth 6
        $utf8NoBom = [Text.UTF8Encoding]::new($false)
        $temporaryState = "$documentStatePath.$PID.tmp"
        [IO.File]::WriteAllText($temporaryState, $documentState + [Environment]::NewLine, $utf8NoBom)
        Move-Item -LiteralPath $temporaryState -Destination $documentStatePath -Force

        [IO.File]::WriteAllText($commitMarker, $commit + [Environment]::NewLine, $utf8NoBom)
        $installedCommit = (Get-Content -LiteralPath $commitMarker -Raw -Encoding UTF8).Trim()
        if ($installedCommit -ne $commit) { throw "Installed commit marker mismatch." }
        if ((Get-FileHash -Algorithm SHA256 -LiteralPath $currentProjectPath).Hash -ne $variantHash) {
            throw "Installed H03V current project hash mismatch."
        }
    }
    catch [UnauthorizedAccessException] {
        Write-Error "P64-V2H03V local project handoff write blocked: $($_.Exception.Message)"
        exit 21
    }
    catch [IO.IOException] {
        Write-Error "P64-V2H03V local project handoff write blocked: $($_.Exception.Message)"
        exit 21
    }
}

Write-Output ""
Write-Output "P64-V2H03V Fusion actions remaining:"
Write-Output "1. Recharger l add-in 0.1.55 et ouvrir BGIG. Le projet P64-V2H03V multi-container variant dead end doit etre charge avec Auto intelligent + Rapide."
Write-Output "2. Attendre l apercu : il doit afficher Solution trouvee, deux bacs et une proposition materialisable. Ne pas cliquer Materialiser dans Fusion."
Write-Output "3. Ouvrir Diagnostic du calcul puis Variantes internes. Confirmer free_3d_beam, une voie Rapide, deux variantes internes non canoniques, un certificat global Oui, des budgets/compteurs lisibles, Canonique execute d abord = Oui et Produit cartesien materialise = Non."
Write-Output "4. Confirmer que le diagnostic secondaire reste replie par defaut et que la palette reste stable. Le calcul et le changement de document ne creent aucune scene."
Write-Output "5. Ouvrir le document recent p64-v2h03v-simple-control.bgig.json : il doit rester Solution trouvee via Etages et piles, sans section Variantes internes."
Write-Output "6. Si tu verifies aussi un cas dense non resolu, son statut doit rester no_solution_within_budget, jamais une impossibilite deduite du seul volume positif."
Write-Output "7. Confirmer qu aucun corps Fusion ne change avant Materialiser dans Fusion. Cette gate ne calibre aucune valeur physique et reste print-validated: false."
Write-Output "8. Reply: P64-V2H03V Fusion OK 0.1.55 - commit $commit, or contextual KO with project, method, effort, visible status and diagnostic."
Write-Output "Prepared P64-V2H03V Fusion test: $(-not $DryRun)"
