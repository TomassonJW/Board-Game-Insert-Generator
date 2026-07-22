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
$preflight = Join-Path $root "scripts\fusion\p64_l04v_preflight.py"
$projectDirectory = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "BGIG\projects"
$fixturePath = Join-Path $projectDirectory "p64-l04v-pocket-baseline.bgig.json"
$commitMarker = Join-Path $target "bgig_installed_commit.txt"

if (-not (Test-Path -LiteralPath $preflight -PathType Leaf)) {
    throw "P64-L04V preflight script missing: $preflight"
}

Write-Output "BGIG P64-L04V combined Fusion gate preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"
Write-Output "Baseline fixture: $fixturePath"

$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $root "src"
    foreach ($pattern in @(
        "test_incremental_layout_reuse.py",
        "test_operation_activity.py",
        "test_fusion_palette_project.py",
        "test_fusion_palette_cad_sync.py",
        "test_fusion_palette_dom.py",
        "test_fusion_palette_qt_transport.py"
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
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.58"') {
        throw "Installed P64-L04V package mismatch: expected 0.1.58."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        "operation-activity",
        "operation_started_at_ms",
        "operationWatchdogMs",
        "operationKindActive",
        "bgig.operation_activity.v1",
        ("Raison d" + [char]0x2019 + "arr" + [char]0x00EA + "t"),
        ("R" + [char]0x00E9 + "ponse obsol" + [char]0x00E8 + "te ou invalid" + [char]0x00E9 + "e")
    )) {
        if (-not $palette.Contains($marker)) {
            throw "Installed P64-L04V palette marker missing: $marker"
        }
    }
    foreach ($relativeRuntime in @(
        "lib\board_game_insert_generator\incremental_layout_reuse.py",
        "lib\board_game_insert_generator\operation_activity.py",
        "lib\board_game_insert_generator\staged_calculation.py"
    )) {
        if (-not (Test-Path -LiteralPath (Join-Path $target $relativeRuntime) -PathType Leaf)) {
            throw "Installed P64-L04V runtime missing: $relativeRuntime"
        }
    }
    $utf8NoBom = [Text.UTF8Encoding]::new($false)
    [IO.File]::WriteAllText($commitMarker, $commit + [Environment]::NewLine, $utf8NoBom)
    $installedCommit = (Get-Content -LiteralPath $commitMarker -Raw -Encoding UTF8).Trim()
    if ($installedCommit -ne $commit) { throw "Installed commit marker mismatch." }
    if (-not (Test-Path -LiteralPath $fixturePath -PathType Leaf)) {
        throw "P64-L04V baseline fixture was not created: $fixturePath"
    }
}

Write-Output ""
Write-Output "P64-L04V Fusion actions remaining:"
Write-Output "1. Recharger l add-in 0.1.58 puis ouvrir la palette BGIG dans un document Fusion vide."
Write-Output "2. Ouvrir le projet p64-l04v-pocket-baseline.bgig.json depuis le dossier BGIG/projects de Documents."
Write-Output "3. Calculer le plan minimal, puis materialiser. Observer activite immediate, etape, temps ecoule, aucun pourcentage ni bouton Annuler."
Write-Output "4. Garder ou creer hors BGIG un corps TEMOIN_UTILISATEUR dans la scene Fusion."
Write-Output "5. Dans Bac L04, ajouter un petit element 8 x 16 x 8 mm. Verifier placement_reused, compteur solveur global a zero et voisins inchanges."
Write-Output "6. Ajouter ensuite un element 20 x 20 x 10 mm. Verifier fallback explicite, plan stale et aucun solve global automatique."
Write-Output "7. Lancer Calculer explicitement, verifier la scene stale, puis Mettre a jour la scene. Verifier une seule scene BGIG et TEMOIN_UTILISATEUR conserve."
Write-Output "8. Relever provenance, methode, effort, budgets, phases, incumbent et raison d arret."
Write-Output "9. Reply: P64-L04V Fusion OK 0.1.58 - commit $commit, or contextual KO with step, visible status and diagnostic."
Write-Output "Prepared P64-L04V Fusion gate: $(-not $DryRun)"
