param(
    [string] $RepoRoot,
    [string] $TargetPath,
    [ValidateSet("compact_only", "compact_and_exploded")]
    [string] $GenerationMode = "compact_only",
    [string] $AssetsText = "coin-tokens,tokens,40,18,16,2,loose; status-tokens,tokens,23,10,35,2,loose",
    [switch] $DryRun
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_fusion_helpers.ps1"

$root = Resolve-BgigRepoRoot -RepoRoot $RepoRoot
$target = Get-BgigFusionAddinTargetPath -TargetPath $TargetPath
$commit = Get-BgigCurrentCommit -RepoRoot $root

Write-Output "BGIG quick asset Fusion smoke test preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"
Write-Output "Generation mode: $GenerationMode"
Write-Output "Assets text: $AssetsText"

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$settings = @{
    action = "generate"
    input_mode = "quick_asset_box"
    generation_mode = $GenerationMode
    project_root = $root
    box_inner_x_mm = "130"
    box_inner_y_mm = "50"
    box_inner_z_mm = "60"
    grid_units_x = "4"
    grid_units_y = "4"
    grid_units_z = "3"
    wall_thickness_mm = "1.2"
    floor_thickness_mm = "1.2"
    peripheral_clearance_mm = "0.4"
    inter_module_clearance_mm = "0.3"
    print_profile = "draft"
    quick_asset_box_assets_text = $AssetsText
}
Write-BgigFusionUiSettings -TargetPath $target -Settings $settings -DryRun:$DryRun

Write-Output ""
Write-Output "Recommended P13 quick asset values:"
Write-Output "- input_mode: quick_asset_box"
Write-Output "- box_inner_mm: 130 x 50 x 60"
Write-Output "- grid_units: 4 x 4 x 3"
Write-Output "- wall_thickness_mm: 1.2"
Write-Output "- floor_thickness_mm: 1.2"
Write-Output "- peripheral_clearance_mm: 0.4"
Write-Output "- inter_module_clearance_mm: 0.3"
Write-Output "- print_profile: draft (quick_asset_box temporary config maps this UI alias to engine profile fast_draft)"
Write-Output "- assets: $AssetsText"
Write-Output ""
Write-Output "Fusion actions remaining:"
Write-Output "1. Open Fusion 360 and an Assembly-compatible design."
Write-Output "2. Run BoardGameInsertGenerator or click Generate Board Game Insert."
Write-Output "3. In the UI settings block, confirm UI settings loaded: yes."
Write-Output "4. Confirm Loaded input mode = quick_asset_box and Loaded generation mode = $GenerationMode."
Write-Output "5. Confirm the Assets (quick_asset_box) field contains the prepared assets."
Write-Output "6. Confirm Action = generate, or regenerate if a BGIG scene already exists."
Write-Output "7. Run generation and verify Quick asset box inputs, assets_read, asset_items_visualized: no, asset_cavities_generated: yes, asset_cavity_policy: per_source_asset_rectangular_compartments_v0, asset_fit_cavities_planned: 2, asset_compartments_generated: yes, asset_compartment_cavities_planned: 2, asset_compartment_debug_outlines: yes, count_aware_storage_sizing: yes, asset_debug_visualization: yes, asset_sizing capacity_per_stack/pile_count diagnostics, module_candidate_sizing declared_capacity and module_size 52.8 x 39.0 x 48.0, two asset_cavity entries for coin-tokens and status-tokens, cavity sizes about 37.6 x 17.6 x 46.8 mm and 11.6 x 36.6 x 46.8 mm, retained_floor 1.2 mm, internal_wall 1.2 mm on the second compartment, Reference outline policy: bottom_and_top_box_xy_outlines, Body sizing report, Registry validation: ok, and Print validation: false."
Write-Output "8. Reopen BGIG and confirm the asset text is still present."
Write-Output "9. Modify one asset or dimension, set Action = regenerate, run, and verify the scene is replaced without duplicates."
Write-Output "10. Run clear_bgig_scene and verify non-BGIG objects are preserved."
Write-Output "Prepared quick asset test: $(-not $DryRun)"
