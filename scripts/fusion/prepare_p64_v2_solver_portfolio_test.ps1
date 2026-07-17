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

Write-Output "BGIG P64-V2 solver portfolio product-gate preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.51"') {
        throw "Installed P64-H08 package mismatch: expected 0.1.51."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        'id="solver-method"',
        'id="solver-effort"',
        'id="solver-ranking"',
        'save_solver_settings',
        'function solverTelemetryDetails',
        'renderBackgroundUpdate(action)'
    )) {
        if (-not $palette.Contains($marker)) {
            throw "Installed P64-H08 palette marker missing: $marker"
        }
    }
    $bridge = Get-Content -LiteralPath (Join-Path $target "palette_project.py") -Raw -Encoding UTF8
    foreach ($marker in @('"save_solver_settings"', 'solver_method=solver_settings["method"]', 'effort_profile=solver_settings["effort"]')) {
        if (-not $bridge.Contains($marker)) {
            throw "Installed P64-H08 bridge marker missing: $marker"
        }
    }
    $solver = Get-Content -LiteralPath (Join-Path $target "lib\board_game_insert_generator\partition_solver.py") -Raw -Encoding UTF8
    foreach ($marker in @('def solve_partition_plan(', 'solver_method: str | None = None', 'def _portfolio_public_plan(')) {
        if (-not $solver.Contains($marker)) {
            throw "Installed P64-H08 solver marker missing: $marker"
        }
    }
}

Write-Output ""
Write-Output "P64-V2 Fusion actions remaining:"
Write-Output "1. Recharger l add-in puis ouvrir Reglages > Recherche. Confirmer les choix Auto intelligent, Etages et piles, Placement 3D libre, et Rapide / Normal / Approfondi."
Write-Output "2. Sur un projet non trivial, conserver Auto intelligent + Normal, recalculer, puis ouvrir Diagnostic du calcul : methode, effort, temps et famille retenue doivent etre coherents."
Write-Output "3. Choisir Etages et piles puis Placement 3D libre. A chaque fois, attendre l apercu adaptatif ou cliquer Recalculer maintenant ; le diagnostic doit nommer le choix courant et aucune proposition non certifiee ne doit etre materialisable."
Write-Output "4. Revenir a Auto intelligent et choisir Approfondi sur un cas dense. Verifier que le resultat reste explicite : solution certifiee, absence de solution dans le budget, impossibilite prouvee, ou reponse obsolete."
Write-Output "5. Editer rapidement deux champs de projet, selectionner le contenu du second et taper pendant autosave, validation et apercu : le focus et la selection doivent rester stables."
Write-Output "6. Confirmer qu aucun corps Fusion ne change avant Materialiser dans Fusion. Cette gate ne valide ni valeurs physiques ni impression."
Write-Output "7. Reply: P64-V2 Fusion OK 0.1.51 - commit $commit, or contextual KO."
Write-Output "Prepared P64-V2 Fusion test: $(-not $DryRun)"