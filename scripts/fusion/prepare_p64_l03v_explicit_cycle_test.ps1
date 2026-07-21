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
$commitMarker = Join-Path $target "bgig_installed_commit.txt"

Write-Output "BGIG P64-L03V explicit staged-cycle Fusion gate preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $root "src"
    foreach ($pattern in @(
        "test_staged_calculation.py",
        "test_fusion_palette_project.py",
        "test_fusion_palette_dom.py",
        "test_fusion_palette_result.py"
    )) {
        & $python -m unittest discover -s (Join-Path $root "tests") -p $pattern
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
}
finally {
    $env:PYTHONPATH = $previousPythonPath
}

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.56"') {
        throw "Installed P64-L03V package mismatch: expected 0.1.56."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        "primary-calculation-action",
        "Calculer l’agencement",
        "Finaliser le volume",
        "finalize_project",
        "staged_calculation"
    )) {
        if (-not $palette.Contains($marker)) {
            throw "Installed P64-L03V palette marker missing: $marker"
        }
    }
    foreach ($forbidden in @(
        "AUTO_SOLVE_STABILITY_MS",
        "scheduleAdaptiveSolve",
        "autoSolveTimer"
    )) {
        if ($palette.Contains($forbidden)) {
            throw "Installed P64-L03V automatic-solve marker still present: $forbidden"
        }
    }
    $stagedRuntime = Join-Path $target "lib\board_game_insert_generator\staged_calculation.py"
    if (-not (Test-Path -LiteralPath $stagedRuntime -PathType Leaf)) {
        throw "Installed P64-L03V staged runtime missing: $stagedRuntime"
    }
    $utf8NoBom = [Text.UTF8Encoding]::new($false)
    [IO.File]::WriteAllText($commitMarker, $commit + [Environment]::NewLine, $utf8NoBom)
    $installedCommit = (Get-Content -LiteralPath $commitMarker -Raw -Encoding UTF8).Trim()
    if ($installedCommit -ne $commit) { throw "Installed commit marker mismatch." }
}
else {
    Write-Output "Dry run: would install and verify the explicit staged runtime."
    Write-Output "Dry run: would write installed commit marker at $commitMarker"
}

Write-Output ""
Write-Output "P64-L03V Fusion actions remaining:"
Write-Output "1. Recharger l add-in 0.1.56 et ouvrir un projet simple deja calculable."
Write-Output "2. Modifier une dimension locale. Confirmer que les possibilites locales se mettent a jour sans calcul global, sans perte de focus et sans scene."
Write-Output "3. Cliquer Calculer l agencement. Confirmer que l ancien apercu reste honnetement obsolete pendant le calcul, puis que le bouton devient Finaliser le volume."
Write-Output "4. Confirmer qu aucune scene Fusion n est creee et que Materialiser dans Fusion reste indisponible avant finalisation."
Write-Output "5. Cliquer Finaliser le volume. Confirmer que le plan final devient pret sans changement visible de geometrie ni corps automatique."
Write-Output "6. Modifier a nouveau une dimension. Confirmer que le plan final devient obsolete et qu une materialisation directe est refusee."
Write-Output "7. Recalculer, finaliser, puis cliquer Materialiser dans Fusion. Confirmer que la scene est creee seulement a cette derniere action."
Write-Output "8. Confirmer que les details techniques restent replies par defaut et que les methodes, budgets et stop reasons restent observables."
Write-Output "9. Reply: P64-L03V Fusion OK 0.1.56 - commit $commit, or contextual KO with project, step, visible status and diagnostic."
Write-Output "Prepared P64-L03V Fusion test: $(-not $DryRun)"
