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

Write-Output "BGIG quick parametric Fusion smoke test preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$settings = @{
    action = "generate"
    input_mode = "quick_parametric_box"
    generation_mode = "compact_only"
    project_root = $root
    box_inner_x_mm = "120"
    box_inner_y_mm = "80"
    box_inner_z_mm = "30"
    grid_units_x = "4"
    grid_units_y = "4"
    grid_units_z = "3"
    wall_thickness_mm = "1.2"
    floor_thickness_mm = "1.2"
    peripheral_clearance_mm = "0.4"
    inter_module_clearance_mm = "0.3"
    print_profile = "draft"
}
Write-BgigFusionUiSettings -TargetPath $target -Settings $settings -DryRun:$DryRun

Write-Output ""
Write-Output "Recommended P12-M004V values:"
Write-Output "- box_inner_mm: 120 x 80 x 30"
Write-Output "- grid_units: 4 x 4 x 3"
Write-Output "- wall_thickness_mm: 1.2"
Write-Output "- floor_thickness_mm: 1.2"
Write-Output "- peripheral_clearance_mm: 0.4"
Write-Output "- inter_module_clearance_mm: 0.3"
Write-Output "- print_profile: draft"
Write-Output ""
Write-Output "Fusion actions remaining:"
Write-Output "1. Open Fusion 360 and an Assembly-compatible design."
Write-Output "2. Run BoardGameInsertGenerator or click Generate Board Game Insert."
Write-Output "3. Confirm Input mode = quick_parametric_box and Action = generate."
Write-Output "4. Run generation, reopen BGIG, confirm all values are rehydrated."
Write-Output "5. Change box_inner_x_mm to 160, set Action = regenerate, run."
Write-Output "6. Reopen BGIG and confirm 160 is still present."
Write-Output "7. Run clear_bgig_scene and verify non-BGIG objects are preserved."
Write-Output "Prepared quick parametric test: $(-not $DryRun)"
