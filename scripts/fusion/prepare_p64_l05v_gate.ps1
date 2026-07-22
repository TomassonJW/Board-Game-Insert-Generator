param(
    [string] $RepoRoot,
    [string] $TargetPath,
    [switch] $DryRun
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_fusion_helpers.ps1"

$root = Resolve-BgigRepoRoot -RepoRoot $RepoRoot
$source = Get-BgigAddinSourcePath -RepoRoot $root
$target = Get-BgigFusionAddinTargetPath -TargetPath $TargetPath
$commit = Get-BgigCurrentCommit -RepoRoot $root
$python = (Get-Command python -ErrorAction Stop).Source
$preflight = Join-Path $root "scripts\fusion\p64_l05v_preflight.py"
$projectDirectory = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "BGIG\projects"
$fixturePath = Join-Path $projectDirectory "p64-l05v-global-void-baseline.bgig.json"
$commitMarker = Join-Path $target "bgig_installed_commit.txt"
$manifestPath = Join-Path $source "BoardGameInsertGenerator.manifest"

if (-not (Test-Path -LiteralPath $preflight -PathType Leaf)) {
    throw "P64-L05V preflight script missing: $preflight"
}
$manifestText = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8
$versionMatch = [regex]::Match($manifestText, '"version"\s*:\s*"(?<version>[^"]+)"')
if (-not $versionMatch.Success) {
    throw "Source add-in manifest has no readable version: $manifestPath"
}
$expectedVersion = $versionMatch.Groups["version"].Value

Write-Output "BGIG P64-L05V Fusion gate preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Package version: $expectedVersion"
Write-Output "Target: $target"
Write-Output "Baseline fixture: $fixturePath"

$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $root "src"
    foreach ($pattern in @(
        "test_incremental_global_container_reuse.py",
        "test_solver_case_bundle.py",
        "test_certified_plan_witness.py",
        "test_fusion_palette_project.py",
        "test_fusion_palette_dom.py",
        "test_p64_l05v_preflight.py"
    )) {
        & $python -m unittest discover -s (Join-Path $root "tests") -p $pattern
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    if ($DryRun) {
        & $python $preflight
    }
    else {
        & $python $preflight --write-fixture $fixturePath
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

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    & "$PSScriptRoot\check_installed_addin.ps1" -TargetPath $target -ExpectedVersion $expectedVersion
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    $installedManifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($installedManifest -notmatch ('"version"\s*:\s*"' + [regex]::Escape($expectedVersion) + '"')) {
        throw "Installed P64-L05V package mismatch: expected $expectedVersion."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        "dev-solver-case-capture",
        "capture_solver_case",
        "SolverCaseBundle",
        "certified-witness-diagnostics",
        "container_placed_in_global_void",
        "global_void_reuse",
        "bgig.operation_activity.v1"
    )) {
        if (-not $palette.Contains($marker)) {
            throw "Installed P64-L05V palette marker missing: $marker"
        }
    }
    foreach ($relativeRuntime in @(
        "lib\board_game_insert_generator\incremental_global_container_reuse.py",
        "lib\board_game_insert_generator\solver_case_bundle.py",
        "lib\board_game_insert_generator\certified_plan_witness.py",
        "lib\board_game_insert_generator\operation_activity.py",
        "lib\board_game_insert_generator\staged_calculation.py"
    )) {
        if (-not (Test-Path -LiteralPath (Join-Path $target $relativeRuntime) -PathType Leaf)) {
            throw "Installed P64-L05V runtime missing: $relativeRuntime"
        }
    }
    $utf8NoBom = [Text.UTF8Encoding]::new($false)
    [IO.File]::WriteAllText($commitMarker, $commit + [Environment]::NewLine, $utf8NoBom)
    $installedCommit = (Get-Content -LiteralPath $commitMarker -Raw -Encoding UTF8).Trim()
    if ($installedCommit -ne $commit) {
        throw "Installed commit marker mismatch."
    }
    if (-not (Test-Path -LiteralPath $fixturePath -PathType Leaf)) {
        throw "P64-L05V baseline fixture was not created: $fixturePath"
    }
}

Write-Output ""
Write-Output "P64-L05V Fusion actions remaining:"
Write-Output "1. Recharger l add-in $expectedVersion, puis ouvrir la palette BGIG dans Fusion."
Write-Output "2. Ouvrir p64-l05v-global-void-baseline.bgig.json depuis Documents/BGIG/projects."
Write-Output "3. Calculer, puis materialiser le plan minimal pour creer le premier witness certifie."
Write-Output "4. Ajouter un nouveau conteneur Nouveau bac avec un element 8 x 8 x 8 mm."
Write-Output "5. Verifier Nouveau conteneur integre, voisins conserves, solve global a zero et details de recertification."
Write-Output "6. Modifier temporairement l effort, revenir a Rapide et relancer Calculer. Verifier witness accepte, recherche poursuivie et cache non revendique."
Write-Output "7. Cliquer DEV Capturer le cas. Verifier le bundle local, sans calcul, finalisation, CAD ni scene."
Write-Output "8. Relever identite, lanes, budgets, temps et raison d arret ; ne pas ajouter le bundle au depot."
Write-Output "9. Reply: P64-L05V Fusion OK $expectedVersion - commit $commit, or contextual KO with step, visible status and diagnostic."
Write-Output "Prepared P64-L05V Fusion gate: $(-not $DryRun)"
