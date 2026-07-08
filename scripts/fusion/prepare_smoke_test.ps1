param(
    [string] $RepoRoot,
    [string] $ConfigPath = "examples/simple_asset_product_scene.json",
    [ValidateSet("compact_only", "compact_and_exploded")]
    [string] $GenerationMode = "compact_only",
    [string] $TargetPath,
    [switch] $DryRun
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_fusion_helpers.ps1"

$root = Resolve-BgigRepoRoot -RepoRoot $RepoRoot
$target = Get-BgigFusionAddinTargetPath -TargetPath $TargetPath
$commit = Get-BgigCurrentCommit -RepoRoot $root
$resolvedConfig = Resolve-Path -LiteralPath (Join-Path $root $ConfigPath) -ErrorAction SilentlyContinue
if (-not $resolvedConfig) {
    $resolvedConfig = Resolve-Path -LiteralPath $ConfigPath -ErrorAction Stop
}

$safeName = [System.IO.Path]::GetFileNameWithoutExtension($resolvedConfig.Path)
$cadIrPath = Join-Path $env:TEMP ("bgig-{0}-{1}.cad-ir.json" -f $safeName, $commit)

Write-Output "BGIG Fusion smoke test preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Config: $($resolvedConfig.Path)"
Write-Output "Generation mode: $GenerationMode"
Write-Output "CAD IR output: $cadIrPath"

Export-BgigCadIr -RepoRoot $root -ConfigPath $resolvedConfig.Path -OutputPath $cadIrPath -DryRun:$DryRun
& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$settings = @{
    action = "generate"
    input_mode = "cad_ir_file"
    generation_mode = $GenerationMode
    cad_ir_path = $cadIrPath
    config_json_path = $resolvedConfig.Path
    project_root = $root
}
Write-BgigFusionUiSettings -TargetPath $target -Settings $settings -DryRun:$DryRun

Write-Output ""
Write-Output "Fusion actions remaining:"
Write-Output "1. Open Fusion 360 and an Assembly-compatible design."
Write-Output "2. Run BoardGameInsertGenerator from Utilities > Add-ins or click Generate Board Game Insert."
Write-Output "3. Confirm Input mode = cad_ir_file, Action = generate, Generation mode = $GenerationMode."
Write-Output "4. Confirm CAD IR path = $cadIrPath."
Write-Output "5. Click Run and verify registry ok, expected occurrences, Body sizing report, and Print validation: false."
Write-Output "Prepared smoke test: $(-not $DryRun)"
