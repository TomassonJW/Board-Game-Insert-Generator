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

Write-Output "BGIG P44-M005 creation and presets preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $DryRun) {
    Assert-BgigPaletteProjectRuntime -AddinPath $target
    $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
    if ($manifest -notmatch '"version"\s*:\s*"0\.1\.28"') {
        throw "Installed P44-M005 package mismatch: expected 0.1.28."
    }
    $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
    foreach ($marker in @('id="creation-preset"', 'id="creation-destination"', 'data-action="add-selected-content"', 'Nouveau conteneur lié')) {
        if ($palette -notlike "*$marker*") { throw "Installed P44-M005 palette marker missing: $marker" }
    }
}

Write-Output ""
Write-Output "P44-M005 Fusion actions remaining:"
Write-Output "1. Ouvre Fusion 360 puis BGIG ; aucun navigateur externe ne doit s ouvrir."
Write-Output "2. Choisis un preset BGIG, Nouveau conteneur lié puis Ajouter."
Write-Output "3. Choisis ensuite un conteneur existant et vérifie qu aucun second conteneur n est créé."
Write-Output "4. Vérifie un preset personnel, son ajout, le raccourci + local et sa suppression."
Write-Output "5. Confirme qu aucun complément, calcul ou scène Fusion ne se déclenche seul."
Write-Output "6. Réponds P44-M005 Fusion OK 0.1.28 - commit <sha>, ou un KO contextualisé."
Write-Output "Prepared P44-M005 Fusion test: $(-not $DryRun)"
