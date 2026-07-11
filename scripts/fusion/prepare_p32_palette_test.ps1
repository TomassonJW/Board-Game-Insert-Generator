param(
    [string] $RepoRoot,
    [ValidateSet("mixed-box", "card-game", "board-game")]
    [string] $StarterId = "mixed-box",
    [string] $TargetPath,
    [switch] $DryRun
)

$ErrorActionPreference = "Stop"

& "$PSScriptRoot\prepare_local_composer_selection_test.ps1" `
    -RepoRoot $RepoRoot `
    -StarterId $StarterId `
    -GenerationMode compact_only `
    -TargetPath $TargetPath `
    -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Output ""
Write-Output "P32 palette Fusion actions remaining:"
Write-Output "1. Ouvre ou cree un design Assembly-compatible dans Fusion 360."
Write-Output "2. Lance BoardGameInsertGenerator depuis Utilities > Add-Ins."
Write-Output "3. Verifie que la petite palette BGIG - Atelier de rangement apparait sans gros formulaire technique."
Write-Output "4. Verifie les cartes Design, Scene Fusion et Fabrication, dont impression non validee."
Write-Output "5. Clique Previsualiser, puis Reglages experts : le formulaire historique ne doit apparaitre qu a ce moment-la."
Write-Output "6. Ferme le formulaire expert, clique Mettre a jour la scene et verifie les trois bacs ouverts existants."
Write-Output "7. Clique Exporter les bacs seulement si tu acceptes la creation des fichiers STL et du manifeste local."
Write-Output "8. Reponds P32 Fusion OK si tout est clair et fonctionne, sinon P32 Fusion KO avec ce que tu vois."
Write-Output "Prepared P32 Fusion palette smoke test: $(-not $DryRun)"