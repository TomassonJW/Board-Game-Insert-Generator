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
$completeFixture = Join-Path $root "scripts\fusion\p66_mvp_complete_project.json"
$impossibleFixture = Join-Path $root "scripts\fusion\p66_mvp_impossible_project.json"
$preflightScript = Join-Path $root "scripts\fusion\p66_preflight.py"
$evidenceRoot = Join-Path ([IO.Path]::GetTempPath()) "bgig-p66-preflight-$commit"
$projectDirectory = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "BGIG\projects"
$projectPath = Join-Path $projectDirectory "bgig_project_v1.json"
$projectBackupPath = Join-Path $projectDirectory "bgig_project_v1.before-p66.json"
$preflightReportPath = Join-Path $projectDirectory "p66_preflight_report.json"
$commitMarker = Join-Path $target "bgig_installed_commit.txt"

$expected = @{
    source_digest = "57a4ac8b4119c6d6fa22ae714884c71addadc19ecc375642821b55b36fff7e05"
    plan_digest = "b5bf4e9c164642bfacc51bec038421827a1d30738f22149d2a00e6603d8abc9e"
    cad_digest = "d5875dd560805a6420222e115b652027c24cb2e358442266fc1c3cd020025d7b"
}

function Read-P66Json {
    param([Parameter(Mandatory = $true)][string] $Path)
    return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Assert-P66CompleteEvidence {
    param([Parameter(Mandatory = $true)][string] $Directory)

    $summary = Read-P66Json -Path (Join-Path $Directory "preflight_summary.json")
    $partition = Read-P66Json -Path (Join-Path $Directory "partition_plan.json")
    $cad = Read-P66Json -Path (Join-Path $Directory "cad_build.json")
    $fusion = Read-P66Json -Path (Join-Path $Directory "fusion_generation_plan.json")
    if ($summary.status -ne "constructed" -or -not $summary.materializable -or -not $summary.cad_ready -or -not $summary.fusion_plan_ready) {
        throw "P66 complete preflight is not materializable."
    }
    if ($summary.source_digest -ne $expected.source_digest -or $summary.plan_digest -ne $expected.plan_digest -or $summary.cad_digest -ne $expected.cad_digest) {
        throw "P66 complete preflight digest mismatch."
    }
    if ($partition.summary.final_body_count -ne 8 -or $partition.summary.stage_count -ne 2 -or $partition.summary.automatic_body_count -ne 0 -or $partition.summary.explicit_complement_count -ne 0) {
        throw "P66 complete partition counts mismatch."
    }
    if ($cad.status -ne "ready_for_fusion" -or $cad.materialization.component_count -ne 8 -or $cad.materialization.cavity_count -ne 9 -or $cad.materialization.top_inset_cut_count -ne 7) {
        throw "P66 complete CAD evidence mismatch."
    }
    if ($fusion.compact_occurrences.Count -ne 8 -or $fusion.exploded_occurrences.Count -ne 0 -or $fusion.cavity_cuts.Count -ne 16) {
        throw "P66 complete Fusion plan evidence mismatch."
    }
    return $summary
}

function Assert-P66ImpossibleEvidence {
    param([Parameter(Mandatory = $true)][string] $Directory)

    $summary = Read-P66Json -Path (Join-Path $Directory "preflight_summary.json")
    $partition = Read-P66Json -Path (Join-Path $Directory "partition_plan.json")
    $cad = Read-P66Json -Path (Join-Path $Directory "cad_build.json")
    if ($summary.status -ne "impossible" -or $summary.materializable -or $summary.cad_ready -or $summary.fusion_plan_ready) {
        throw "P66 impossible fixture must remain blocked."
    }
    if ($cad.status -ne "impossible" -or $cad.materialization.component_count -ne 0) {
        throw "P66 impossible fixture emitted CAD evidence."
    }
    if (-not ($partition.diagnostics | Where-Object { $_.code -eq "CONTAINER_MINIMUM_BLOCKED" -and $_.reference_id -eq "too-small" })) {
        throw "P66 impossible fixture lacks its local corrective diagnostic."
    }
    return $summary
}

foreach ($required in @($completeFixture, $impossibleFixture, $preflightScript)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "P66 required artifact missing: $required"
    }
}

Write-Output "BGIG P66 Fusion-only MVP acceptance preparation"
Write-Output "Repo root: $root"
Write-Output "Commit: $commit"
Write-Output "Target: $target"
Write-Output "Evidence: $evidenceRoot"

$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $root "src"
    & $python -m unittest discover -s (Join-Path $root "tests") -p "test_p66_acceptance_prep.py"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Remove-Item -LiteralPath $evidenceRoot -Recurse -Force -ErrorAction SilentlyContinue
    & $python $preflightScript $completeFixture --output-dir (Join-Path $evidenceRoot "complete")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $python $preflightScript $impossibleFixture --output-dir (Join-Path $evidenceRoot "impossible")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $completeSummary = Assert-P66CompleteEvidence -Directory (Join-Path $evidenceRoot "complete")
    $impossibleSummary = Assert-P66ImpossibleEvidence -Directory (Join-Path $evidenceRoot "impossible")
}
finally {
    $env:PYTHONPATH = $previousPythonPath
}

& "$PSScriptRoot\install_addin.ps1" -RepoRoot $root -TargetPath $target -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($DryRun) {
    Write-Output "Dry run: would preserve one different current project at $projectBackupPath"
    Write-Output "Dry run: would atomically install P66 fixture at $projectPath"
    Write-Output "Dry run: would write commit marker at $commitMarker"
    Write-Output "Dry run: would write readable preflight report at $preflightReportPath"
}
else {
    try {
        & "$PSScriptRoot\check_installed_addin.ps1" -TargetPath $target
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

        New-Item -ItemType Directory -Force -Path $projectDirectory | Out-Null
        $fixtureHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $completeFixture).Hash
        if (Test-Path -LiteralPath $projectPath -PathType Leaf) {
            $currentHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $projectPath).Hash
            if ($currentHash -ne $fixtureHash) {
                if (-not (Test-Path -LiteralPath $projectBackupPath -PathType Leaf)) {
                    $backupTemporary = "$projectBackupPath.$PID.tmp"
                    Copy-Item -LiteralPath $projectPath -Destination $backupTemporary -Force
                    Move-Item -LiteralPath $backupTemporary -Destination $projectBackupPath -Force
                    Write-Output "Current project preserved: $projectBackupPath"
                }
                else {
                    Write-Output "Existing P66 project backup preserved: $projectBackupPath"
                }
            }
        }
        $temporaryProject = "$projectPath.$PID.tmp"
        Copy-Item -LiteralPath $completeFixture -Destination $temporaryProject -Force
        Move-Item -LiteralPath $temporaryProject -Destination $projectPath -Force

        $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
        [IO.File]::WriteAllText($commitMarker, $commit + [Environment]::NewLine, $utf8NoBom)
        $installedCommit = (Get-Content -LiteralPath $commitMarker -Raw -Encoding UTF8).Trim()
        if ($installedCommit -ne $commit) { throw "Installed commit marker mismatch." }

        $report = [ordered]@{
            schema_version = "bgig.p66.preflight-report.v1"
            package_version = "0.1.20"
            commit = $commit
            fixture = $completeFixture
            impossible_fixture = $impossibleFixture
            source_digest = $completeSummary.source_digest
            plan_digest = $completeSummary.plan_digest
            cad_digest = $completeSummary.cad_digest
            impossible_status = $impossibleSummary.status
            evidence_root = $evidenceRoot
            installed_commit_marker = $commitMarker
        } | ConvertTo-Json -Depth 6
        $temporaryReport = "$preflightReportPath.$PID.tmp"
        [IO.File]::WriteAllText($temporaryReport, $report + [Environment]::NewLine, $utf8NoBom)
        Move-Item -LiteralPath $temporaryReport -Destination $preflightReportPath -Force
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
Write-Output "P66 Fusion actions remaining: see docs/P66_FUSION_MVP_ACCEPTANCE.md, steps 1 to 21."
Write-Output "Return exactly: P66 Fusion OK 0.1.20 - commit $commit"
Write-Output "Or: P66 Fusion KO - etape <n> - attendu <...> - observe <...> - message <...>"
Write-Output "Prepared P66 Fusion-only MVP acceptance: $(-not $DryRun)"
