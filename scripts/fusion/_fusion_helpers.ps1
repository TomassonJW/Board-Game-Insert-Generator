Set-StrictMode -Version Latest

$script:BgigAddinName = "BoardGameInsertGenerator"
$script:BgigAddinRelativePath = Join-Path "fusion_addin" $script:BgigAddinName
$script:BgigDefaultFusionAddinsRoot = Join-Path $env:APPDATA "Autodesk\Autodesk Fusion 360\API\AddIns"
$script:BgigAppDataBlockedMessage = "Local AppData write blocked. Use Local/Handoff or approve filesystem write."

function Resolve-BgigRepoRoot {
    param(
        [string] $RepoRoot
    )

    if ($RepoRoot) {
        $candidate = Resolve-Path -LiteralPath $RepoRoot -ErrorAction Stop
        return $candidate.Path
    }

    $candidate = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..") -ErrorAction Stop
    $root = $candidate.Path
    $addinPath = Join-Path $root $script:BgigAddinRelativePath
    if (-not (Test-Path -LiteralPath $addinPath -PathType Container)) {
        throw "BGIG repo root could not be resolved from script path. Missing: $addinPath"
    }
    return $root
}

function Get-BgigAddinSourcePath {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RepoRoot
    )

    $source = Join-Path $RepoRoot $script:BgigAddinRelativePath
    if (-not (Test-Path -LiteralPath $source -PathType Container)) {
        throw "Fusion add-in source folder not found: $source"
    }
    return (Resolve-Path -LiteralPath $source -ErrorAction Stop).Path
}

function Get-BgigFusionAddinTargetPath {
    param(
        [string] $TargetPath
    )

    if ($TargetPath) {
        return $TargetPath
    }
    return Join-Path $script:BgigDefaultFusionAddinsRoot $script:BgigAddinName
}

function Get-BgigCurrentCommit {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RepoRoot
    )

    $commit = (& git -C $RepoRoot rev-parse --short HEAD 2>$null)
    if ($LASTEXITCODE -ne 0 -or -not $commit) {
        return "unknown"
    }
    return ($commit | Select-Object -First 1).Trim()
}

function Assert-BgigFusionAddinMarkers {
    param(
        [Parameter(Mandatory = $true)]
        [string] $AddinPath,
        [string[]] $Markers = @(
            "Generate Board Game Insert",
            "quick_parametric_box",
            "quick_asset_box",
            "QUICK_ASSET_BOX_ASSETS_INPUT_ID",
            "QUICK_ASSET_BOX_MAX_STACK_HEIGHT_INPUT_ID",
            "QUICK_ASSET_BOX_TARGET_ASPECT_RATIO_INPUT_ID",
            "QUICK_ASSET_BOX_MAX_MODULE_LENGTH_INPUT_ID",
            "Assets (quick_asset_box)",
            "Max stack height mm (quick_asset_box, optional)",
            "Target aspect ratio (quick_asset_box, optional)",
            "Max module length mm (quick_asset_box, optional)",
            "quick_asset_box_max_stack_height_mm",
            "quick_asset_box_target_aspect_ratio",
            "quick_asset_box_max_module_length_mm",
            "grid_semantics",
            "body_snap_to_grid",
            "stack_height_policy",
            "asset_items_visualized",
            "asset_cavities_generated",
            "asset_cavity_policy",
            "single_asset_fit_rectangular_cavity_v0",
            "per_source_asset_rectangular_compartments_v0",
            "asset_fit_cavities_generated",
            "asset_compartment_cavities_planned",
            "asset_compartment_debug_outlines",
            "per_compartment_top_open_rectangular_notch_v0",
            "asset_access_notches_planned",
            "count_aware_storage_sizing",
            "asset_debug_visualization",
            "stacked_rectangular_piles_v0",
            "inspect_bgig_scene",
            "export_printables",
            "fusion_only_stl_per_printable_module_v0",
            "bgig_export_manifest.json",
            "bgig_export_manifest.md",
            "printability_export_allowed",
            "print_validated: false",
            "bgig_ui_settings.json"
        )
    )

    $entrypoint = Join-Path $AddinPath "BoardGameInsertGenerator.py"
    $skeleton = Join-Path $AddinPath "fusion_skeleton.py"
    if (-not (Test-Path -LiteralPath $entrypoint -PathType Leaf)) {
        throw "Fusion add-in entrypoint missing: $entrypoint"
    }
    if (-not (Test-Path -LiteralPath $skeleton -PathType Leaf)) {
        throw "Fusion add-in skeleton missing: $skeleton"
    }

    $text = (Get-Content -LiteralPath $entrypoint -Raw -Encoding UTF8) + "`n" + (Get-Content -LiteralPath $skeleton -Raw -Encoding UTF8)
    foreach ($marker in $Markers) {
        if ($text -notlike "*$marker*") {
            throw "Installed add-in marker missing: $marker"
        }
    }
}

function Assert-BgigPaletteProjectRuntime {
    param(
        [Parameter(Mandatory = $true)]
        [string] $AddinPath
    )

    $required = @(
        (Join-Path $AddinPath "palette.html"),
        (Join-Path $AddinPath "palette_project.py"),
        (Join-Path $AddinPath "resources\16x16.svg"),
        (Join-Path $AddinPath "resources\32x32.svg"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\project_v1.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\asset_catalog.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\personal_presets.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\project_presets.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\expandable_envelope.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\flat_stack_reservation.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\top_inset_reservation.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\partition_solver.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\solver_settings.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\solver_outcome.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\solver_contract.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\solver_portfolio.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\free_3d_greedy_solver.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\free_3d_continuous_closure.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\free_3d_beam_solver.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\free_3d_plan_adapter.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\volumetric_stage_solver.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\preview_explanations.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\partition_result_view.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\container_sizing_view.py"),
        (Join-Path $AddinPath "lib\board_game_insert_generator\partition_cad.py")
    )
    foreach ($requiredPath in $required) {
        if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
            throw "Installed Fusion-only runtime file missing: $requiredPath"
        }
    }
    $palette = Get-Content -LiteralPath (Join-Path $AddinPath "palette.html") -Raw -Encoding UTF8
    $paletteMarkers = @(
        "bgig.palette.request.v1",
        ("1. Bo" + [char]0x00EE + "te et plateaux"),
        ("2. Conteneurs et " + [char]0x00E9 + "l" + [char]0x00E9 + "ments"),
        ("3. R" + [char]0x00E9 + "glages"),
        ("4. Aper" + [char]0x00E7 + "u"),
        "materialize_project",
        "regenerate_project",
        "bgig_palette_ready",
        "workspace-toolbar",
        "historic-complements",
        "container-primary-grid",
        "group-mode",
        "estimate-groups-action",
        "container_sizing",
        "preview-explanations",
        "presentation",
        "Ordre de retrait",
        "proposal_with_residuals",
        "technical-drawer",
        "solvedStale",
        "primary-calculation-action",
        "finalize_project",
        "staged_calculation",
        "latestDerivedRequest",
        "solver-method",
        "solver-effort",
        "save_solver_settings",
        ("Calculer l" + [char]0x2019 + "agencement")
    )
    foreach ($marker in $paletteMarkers) {
        if ($palette -notlike "*$marker*") {
            throw "Installed palette marker missing: $marker"
        }
    }
    foreach ($forbiddenMarker in @('data-action="add-complement"', 'data-action="add-complement-preset"', 'id="complement-presets"')) {
        if ($palette -like "*$forbiddenMarker*") {
            throw "Installed P66-M000 palette still exposes complement creation: $forbiddenMarker"
        }
    }}
function Assert-BgigTargetUnderAppData {
    param(
        [Parameter(Mandatory = $true)]
        [string] $TargetPath
    )

    $appDataRoot = [System.IO.Path]::GetFullPath($env:APPDATA)
    $fullTarget = [System.IO.Path]::GetFullPath($TargetPath)
    if (-not $fullTarget.StartsWith($appDataRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to install outside APPDATA. Target: $fullTarget"
    }
    if ([System.IO.Path]::GetFileName($fullTarget) -ne $script:BgigAddinName) {
        throw "Refusing to install to a folder not named $($script:BgigAddinName): $fullTarget"
    }
}

function Copy-BgigFusionAddin {
    param(
        [Parameter(Mandatory = $true)]
        [string] $SourcePath,
        [Parameter(Mandatory = $true)]
        [string] $TargetPath,
        [switch] $DryRun
    )

    Assert-BgigTargetUnderAppData -TargetPath $TargetPath
    $parent = Split-Path -Parent $TargetPath

    if ($DryRun) {
        Write-Output "Dry run: would remove installed add-in: $TargetPath"
        Write-Output "Dry run: would copy add-in from: $SourcePath"
        Write-Output "Dry run: would copy add-in to: $TargetPath"
        return
    }

    try {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
        if (Test-Path -LiteralPath $TargetPath) {
            Remove-Item -LiteralPath $TargetPath -Recurse -Force
        }
        Copy-Item -LiteralPath $SourcePath -Destination $parent -Recurse -Force

        # The installed add-in must run without a development checkout or local server.
        $repoRoot = (Resolve-Path -LiteralPath (Join-Path $SourcePath "..\..") -ErrorAction Stop).Path
        $engineSource = Join-Path $repoRoot "src\board_game_insert_generator"
        $engineTarget = Join-Path $TargetPath "lib\board_game_insert_generator"
        if (-not (Test-Path -LiteralPath $engineSource -PathType Container)) {
            throw "BGIG pure engine source missing: $engineSource"
        }
        New-Item -ItemType Directory -Force -Path $engineTarget | Out-Null
        Get-ChildItem -LiteralPath $engineSource -File -Filter "*.py" | Copy-Item -Destination $engineTarget -Force
    }
    catch [System.UnauthorizedAccessException] {
        Write-Error $script:BgigAppDataBlockedMessage
        exit 20
    }
    catch [System.IO.IOException] {
        Write-Error "$($script:BgigAppDataBlockedMessage) Details: $($_.Exception.Message)"
        exit 20
    }
}

function Write-BgigFusionUiSettings {
    param(
        [Parameter(Mandatory = $true)]
        [string] $TargetPath,
        [Parameter(Mandatory = $true)]
        [hashtable] $Settings,
        [switch] $DryRun
    )

    $settingsPath = Join-Path $TargetPath "bgig_ui_settings.json"
    $json = $Settings | ConvertTo-Json -Depth 6
    if ($DryRun) {
        Write-Output "Dry run: would write UI settings: $settingsPath"
        Write-Output $json
        return
    }

    try {
        $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
        [System.IO.File]::WriteAllText($settingsPath, $json + [Environment]::NewLine, $utf8NoBom)
    }
    catch [System.UnauthorizedAccessException] {
        Write-Error $script:BgigAppDataBlockedMessage
        exit 20
    }
    catch [System.IO.IOException] {
        Write-Error "$($script:BgigAppDataBlockedMessage) Details: $($_.Exception.Message)"
        exit 20
    }
}

function Export-BgigCadIr {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RepoRoot,
        [Parameter(Mandatory = $true)]
        [string] $ConfigPath,
        [Parameter(Mandatory = $true)]
        [string] $OutputPath,
        [switch] $DryRun
    )

    if (-not (Test-Path -LiteralPath $ConfigPath -PathType Leaf)) {
        throw "Config file not found: $ConfigPath"
    }

    if ($DryRun) {
        Write-Output "Dry run: would export CAD IR:"
        Write-Output "  Config: $ConfigPath"
        Write-Output "  Output: $OutputPath"
        return
    }

    $env:PYTHONPATH = Join-Path $RepoRoot "src"
    & python -m board_game_insert_generator export-cad-ir $ConfigPath --output $OutputPath
    if ($LASTEXITCODE -ne 0) {
        throw "CAD IR export failed for config: $ConfigPath"
    }
}
