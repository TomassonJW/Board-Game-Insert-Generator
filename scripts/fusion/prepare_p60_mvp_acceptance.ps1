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
$fixture = Join-Path $root "scripts\fusion\p60_mvp_project.json"
$projectDirectory = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "BGIG\projects"
$projectPath = Join-Path $projectDirectory "bgig_project_v1.json"
$commitMarker = Join-Path $target "bgig_installed_commit.txt"

if (-not (Test-Path -LiteralPath $fixture -PathType Leaf)) {
    throw "P60 project fixture missing: $fixture"
}

Write-Output "BGIG P60 Fusion-only MVP acceptance preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"
Write-Output "Project fixture: $fixture"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($DryRun) {
    Write-Output "Dry run: would install project to $projectPath"
    Write-Output "Dry run: would write commit marker to $commitMarker"
}
else {
    try {
        Assert-BgigPaletteProjectRuntime -AddinPath $target
        New-Item -ItemType Directory -Force -Path $projectDirectory | Out-Null
        $temporary = "$projectPath.tmp"
        Copy-Item -LiteralPath $fixture -Destination $temporary -Force
        Move-Item -LiteralPath $temporary -Destination $projectPath -Force
        [IO.File]::WriteAllText($commitMarker, $commit + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
        $installedCommit = (Get-Content -LiteralPath $commitMarker -Raw -Encoding UTF8).Trim()
        if ($installedCommit -ne $commit) { throw "Installed commit marker mismatch." }
    }
    catch [UnauthorizedAccessException] {
        Write-Error "Local AppData write blocked. Use Local/Handoff or approve filesystem write."
        exit 20
    }
    catch [IO.IOException] {
        Write-Error "Local AppData write blocked. Use Local/Handoff or approve filesystem write."
        exit 20
    }
}

Write-Output ""
Write-Output "P60 Fusion actions remaining:"
Write-Output "1. Ouvre un nouveau design Fusion en mode Assembly, puis lance Board Game Insert Generator."
Write-Output "2. Confirme que la palette charge P60 - MVP Fusion-only et que les six vues sont accessibles sans navigateur."
Write-Output "3. Va a Fabrication, clique Calculer la partition et confirme 2 corps finaux, 0 complement, 0 corps automatique."
Write-Output "4. Dans Resultat, verifie la vue dessus, la coupe X/Z, Bac jetons, Bac cartes et les cavites nommees."
Write-Output "5. Clique Materialiser dans Fusion et confirme une seule scene BGIG avec 2 composants compacts et leurs cavites ouvertes."
Write-Output "6. Clique Regenerer la scene BGIG et confirme qu il reste une seule scene et 2 composants, sans doublon."
Write-Output "7. Clique Inspecter, puis Exporter les imprimables ; confirme 2 STL et les manifestes JSON/Markdown."
Write-Output "8. Reponds P60 Fusion OK, ou P60 Fusion KO avec l etape et le message visibles."
Write-Output "Prepared P60 Fusion-only MVP acceptance: $(-not $DryRun)"