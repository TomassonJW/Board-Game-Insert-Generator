param(
    [string] $RepoRoot,
    [string] $TargetPath,
    [ValidateSet("compact_only", "compact_and_exploded")]
    [string] $GenerationMode = "compact_only",
    [ValidateSet("tokens", "dice_meeples_generic", "cards_tokens")]
    [string] $Preset = "tokens",
    [string] $AssetsText,
    [switch] $DryRun
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_fusion_helpers.ps1"

$root = Resolve-BgigRepoRoot -RepoRoot $RepoRoot
$target = Get-BgigFusionAddinTargetPath -TargetPath $TargetPath
$commit = Get-BgigCurrentCommit -RepoRoot $root
$presetPath = Join-Path $PSScriptRoot "quick_asset_presets.json"
$presetCatalog = Get-Content -LiteralPath $presetPath -Raw -Encoding UTF8 | ConvertFrom-Json
$presetConfig = $presetCatalog.presets.$Preset
if ($null -eq $presetConfig) {
    throw "Unknown quick asset preset: $Preset"
}
if (-not $AssetsText) {
    $AssetsText = $presetConfig.assets_text
}

Write-Output "BGIG quick asset Fusion smoke test preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"
Write-Output "Generation mode: $GenerationMode"
Write-Output "Preset: $Preset - $($presetConfig.label)"
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
    box_inner_x_mm = "$($presetConfig.box_inner_mm.x)"
    box_inner_y_mm = "$($presetConfig.box_inner_mm.y)"
    box_inner_z_mm = "$($presetConfig.box_inner_mm.z)"
    grid_units_x = "$($presetConfig.grid_units.x)"
    grid_units_y = "$($presetConfig.grid_units.y)"
    grid_units_z = "$($presetConfig.grid_units.z)"
    wall_thickness_mm = "1.2"
    floor_thickness_mm = "1.2"
    peripheral_clearance_mm = "0.4"
    inter_module_clearance_mm = "0.3"
    print_profile = "draft"
    quick_asset_box_assets_text = $AssetsText
}
Write-BgigFusionUiSettings -TargetPath $target -Settings $settings -DryRun:$DryRun

Write-Output ""
Write-Output "Recommended P14 quick asset preset values:"
Write-Output "- input_mode: quick_asset_box"
Write-Output "- preset: $Preset"
Write-Output "- box_inner_mm: $($presetConfig.box_inner_mm.x) x $($presetConfig.box_inner_mm.y) x $($presetConfig.box_inner_mm.z)"
Write-Output "- grid_units: $($presetConfig.grid_units.x) x $($presetConfig.grid_units.y) x $($presetConfig.grid_units.z)"
Write-Output "- wall_thickness_mm: 1.2"
Write-Output "- floor_thickness_mm: 1.2"
Write-Output "- peripheral_clearance_mm: 0.4"
Write-Output "- inter_module_clearance_mm: 0.3"
Write-Output "- print_profile: draft (quick_asset_box temporary config maps this UI alias to engine profile fast_draft)"
Write-Output "- assets: $AssetsText"
Write-Output "- preset notes: $($presetConfig.notes)"
Write-Output ""
Write-Output "Fusion actions remaining:"
Write-Output "1. Open Fusion 360 and an Assembly-compatible design."
Write-Output "2. Run BoardGameInsertGenerator or click Generate Board Game Insert."
Write-Output "3. In the UI settings block, confirm UI settings loaded: yes."
Write-Output "4. Confirm Loaded input mode = quick_asset_box and Loaded generation mode = $GenerationMode."
Write-Output "5. Confirm the Assets (quick_asset_box) field contains the prepared assets."
Write-Output "6. Confirm Action = generate, or regenerate if a BGIG scene already exists."
Write-Output "7. Run generation and verify Quick asset box inputs, assets_read, asset_items_visualized: no, asset_cavities_generated: yes, asset_cavity_policy: per_source_asset_rectangular_compartments_v0, asset_compartments_generated: yes, asset_access_features_generated: yes, count_aware_storage_sizing: yes, asset_debug_visualization: yes, Body sizing report, Registry validation: ok, and Print validation: false."
Write-Output "8. Preset-specific focus: $($presetConfig.smoke_focus)"
Write-Output "9. Reopen BGIG and confirm the asset text is still present."
Write-Output "10. Modify one asset or dimension, set Action = regenerate, run, and verify the scene is replaced without duplicates."
Write-Output "11. Run clear_bgig_scene and verify non-BGIG objects are preserved."
Write-Output "Prepared quick asset test: $(-not $DryRun)"
