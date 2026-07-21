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

Write-Output "BGIG P64-L03R-V corrective dual-materialization Fusion gate preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $root "src"
    foreach ($pattern in @(
        "test_staged_calculation.py",
        "test_partition_cad.py",
        "test_fusion_palette_project.py",
        "test_fusion_palette_cad_sync.py",
        "test_fusion_palette_dom.py",
        "test_fusion_palette_result.py",
        "test_fusion_skeleton.py"
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
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.57"') {
        throw "Installed P64-L03R-V package mismatch: expected 0.1.57."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @(
        "materializedIdentity",
        "sceneMatchesCurrentArtifact",
        "artifact_kind",
        "cad_ir_digest",
        ("Mat" + [char]0x00E9 + "rialiser les volumes minimaux"),
        ("Mettre " + [char]0x00E0 + " jour la sc" + [char]0x00E8 + "ne"),
        ("Choisir une m" + [char]0x00E9 + "thode de finition")
    )) {
        if (-not $palette.Contains($marker)) {
            throw "Installed P64-L03R-V palette marker missing: $marker"
        }
    }
    foreach ($forbidden in @(
        "AUTO_SOLVE_STABILITY_MS",
        "scheduleAdaptiveSolve",
        "autoSolveTimer",
        "Finalise explicitement le volume avant"
    )) {
        if ($palette.Contains($forbidden)) {
            throw "Installed P64-L03R-V forbidden marker present: $forbidden"
        }
    }
    foreach ($relativeRuntime in @(
        "lib\board_game_insert_generator\staged_calculation.py",
        "lib\board_game_insert_generator\partition_cad.py"
    )) {
        $runtime = Join-Path $target $relativeRuntime
        if (-not (Test-Path -LiteralPath $runtime -PathType Leaf)) {
            throw "Installed P64-L03R-V runtime missing: $runtime"
        }
    }
    $utf8NoBom = [Text.UTF8Encoding]::new($false)
    [IO.File]::WriteAllText($commitMarker, $commit + [Environment]::NewLine, $utf8NoBom)
    $installedCommit = (Get-Content -LiteralPath $commitMarker -Raw -Encoding UTF8).Trim()
    if ($installedCommit -ne $commit) { throw "Installed commit marker mismatch." }
}
else {
    Write-Output "Dry run: would install and verify the corrective dual-materialization runtime."
    Write-Output "Dry run: would write installed commit marker at $commitMarker"
}

Write-Output ""
Write-Output "P64-L03R-V Fusion actions remaining:"
Write-Output "1. Recharger l add-in 0.1.57 et ouvrir un projet simple qui produit au moins deux bacs."
Write-Output "2. Conserver ou creer hors de BGIG un petit corps temoin nomme TEMOIN_UTILISATEUR."
Write-Output "3. Modifier un parametre local. Verifier que l analyse locale se met a jour sans solve global ni mutation de scene."
Write-Output "4. Cliquer Calculer l agencement minimal. Verifier que les bacs restent a leurs dimensions minimales, que le residuel est visible et non imprime, et que Finaliser reste une branche optionnelle."
Write-Output "5. Cliquer Materialiser les volumes minimaux sans finaliser. Verifier une seule scene BGIG, aucun volume automatique et des espaces de boite encore libres."
Write-Output "6. Modifier une dimension. Verifier que l ancienne scene reste visible mais desynchronisee et qu elle n est ni effacee ni regeneree automatiquement."
Write-Output "7. Recalculer. Verifier que l action devient Mettre a jour la scene, puis l executer."
Write-Output "8. Verifier qu il reste exactement une scene BGIG, que la geometrie correspond a la nouvelle revision et que TEMOIN_UTILISATEUR existe toujours."
Write-Output "9. Verifier que l identite technique expose artifact_kind, artifact_digest, partition_plan_digest, cad_ir_digest et source_revision, sans revendication d impression."
Write-Output "10. Reply: P64-L03R-V Fusion OK 0.1.57 - commit $commit, or contextual KO with project, step, visible status and diagnostic."
Write-Output "Prepared P64-L03R-V Fusion test: $(-not $DryRun)"
