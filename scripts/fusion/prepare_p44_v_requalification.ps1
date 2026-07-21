param([string] $RepoRoot,[string] $TargetPath,[switch] $DryRun)
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_fusion_helpers.ps1"
$root = Resolve-BgigRepoRoot -RepoRoot $RepoRoot
$target = Get-BgigFusionAddinTargetPath -TargetPath $TargetPath
$commit = Get-BgigCurrentCommit -RepoRoot $root
$python = (Get-Command python -ErrorAction Stop).Source
$commitMarker = Join-Path $target "bgig_installed_commit.txt"
Write-Output "BGIG P44-V foundation UX requalification preparation"
Write-Output "Runtime package: 0.1.55"
Write-Output "Commit: $commit"
$previousPythonPath = $env:PYTHONPATH
try {
  $env:PYTHONPATH = Join-Path $root "src"
  & $python -m unittest discover -s (Join-Path $root "tests") -p "test_fusion_palette_dom.py"
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  & $python -m unittest discover -s (Join-Path $root "tests") -p "test_p64_v2h03v_fusion_gate.py"
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {$env:PYTHONPATH = $previousPythonPath}
& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if (-not $DryRun) {
  Assert-BgigPaletteProjectRuntime -AddinPath $target
  $manifest = Get-Content -LiteralPath (Join-Path $target "BoardGameInsertGenerator.manifest") -Raw -Encoding UTF8
  if ($manifest -notmatch '"version"\s*:\s*"0\.1\.55"') {throw "Installed P44-V requalification package mismatch: expected 0.1.55."}
  $palette = Get-Content -LiteralPath (Join-Path $target "palette.html") -Raw -Encoding UTF8
  foreach ($marker in @("DERIVE_DEBOUNCE_MS=350","AUTO_SOLVE_STABILITY_MS=1500","renderBackgroundUpdate(action)","deferredDerivedPaint","toggle-all-groups","project.box.usable_height_mm=Math.max(0.0001,designHeightValue())","Recalculer maintenant",'data-bridge="materialize_project"',"container-variant-diagnostics")) {
    if (-not $palette.Contains($marker)) {throw "Installed P44-V requalification palette marker missing: $marker"}
  }
  if (([regex]::Matches($palette,'data-bridge="materialize_project"')).Count -ne 1) {throw "Installed P44-V requalification palette must expose exactly one explicit materialize action."}
  $enc=[Text.UTF8Encoding]::new($false)
  [IO.File]::WriteAllText($commitMarker,$commit+[Environment]::NewLine,$enc)
  if ((Get-Content -LiteralPath $commitMarker -Raw -Encoding UTF8).Trim() -ne $commit) {throw "Installed commit marker mismatch."}
}
Write-Output "P44-V requalification Fusion actions remaining:"
Write-Output "1. Recharger l add-in 0.1.55 puis ouvrir BGIG sans cliquer Materialiser dans Fusion."
Write-Output "2. Dans Boite, Conteneurs, Reglages et Apercu, modifier rapidement trois champs : focus, selection et scroll restent stables ; apres 1,5 s, seul le dernier resultat est visible."
Write-Output "3. Creer puis replier un conteneur ; utiliser Tout replier/Tout deplier ; verifier que son en-tete et ses controles restent accessibles."
Write-Output "4. Ouvrir un projet historique puis un projet d environ 50 conteneurs avec elements : import, identites, overrides et palette restent utilisables."
Write-Output "5. Avec une scene BGIG existante, verifier qu une saisie, un import, une sauvegarde ou un apercu ne modifie aucun corps. Seul Materialiser dans Fusion peut le faire."
Write-Output "6. Reply: P44-V Fusion OK 0.1.55 - commit $commit, or contextual KO with project, action, expected, observed and screenshot."
