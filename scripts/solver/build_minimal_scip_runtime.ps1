[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ArtifactRoot,

    [Parameter(Mandatory = $true)]
    [string]$WorkRoot,

    [Parameter(Mandatory = $true)]
    [string]$VcRedistRoot
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = (Resolve-Path -LiteralPath (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))).Path
$artifactPath = (Resolve-Path -LiteralPath $ArtifactRoot).Path
$redistPath = (Resolve-Path -LiteralPath $VcRedistRoot).Path
$workPath = [IO.Path]::GetFullPath((Join-Path (Get-Location) $WorkRoot))

function Assert-WorkspaceChild {
    param([string]$Path, [string]$Label)
    if (-not $Path.StartsWith($repoRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "$Label must stay below the BGIG workspace: $Path"
    }
}

function Invoke-Checked {
    param([string]$FilePath, [string[]]$ArgumentList)
    Write-Host "RUN $FilePath $($ArgumentList -join ' ')"
    & $FilePath @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath"
    }
}

function Expand-ZipLike {
    param([string]$Source, [string]$Destination, [string]$CopyName)
    $copyPath = Join-Path $workPath $CopyName
    Copy-Item -LiteralPath $Source -Destination $copyPath -Force
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    Expand-Archive -LiteralPath $copyPath -DestinationPath $Destination -Force
}

Assert-WorkspaceChild -Path $workPath -Label 'WorkRoot'
if (Test-Path -LiteralPath $workPath) {
    $existing = @(Get-ChildItem -LiteralPath $workPath -Force)
    if ($existing.Count -ne 0) {
        throw "WorkRoot must be new or empty to avoid a mixed build: $workPath"
    }
} else {
    New-Item -ItemType Directory -Path $workPath -Force | Out-Null
}

$lockPath = Join-Path $repoRoot 'tests\fixtures\p64_l08i_minimal_scip_runtime_audit.v1.json'
$lock = Get-Content -LiteralPath $lockPath -Raw | ConvertFrom-Json
$lockedEntries = @($lock.source_artifacts) + @($lock.build_inputs)
foreach ($entry in $lockedEntries) {
    $archiveNameProperty = $entry.PSObject.Properties['archive_name']
    $name = if ($null -ne $archiveNameProperty) { [string]$archiveNameProperty.Value } else { [string]$entry.name }
    $inputPath = Join-Path $artifactPath $name
    if (-not (Test-Path -LiteralPath $inputPath -PathType Leaf)) {
        throw "Missing locked build input: $name"
    }
    $item = Get-Item -LiteralPath $inputPath
    $digest = (Get-FileHash -LiteralPath $inputPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($item.Length -ne [long]$entry.size_bytes -or $digest -ne [string]$entry.sha256) {
        throw "Locked size or SHA-256 mismatch: $name"
    }
}
Write-Host "LOCKED_INPUTS_OK count=$($lockedEntries.Count)"

$sourceRoot = Join-Path $workPath 'src'
Expand-ZipLike -Source (Join-Path $artifactPath 'scip-v10.0.2.zip') -Destination $sourceRoot -CopyName 'scip-v10.0.2.zip'
Expand-ZipLike -Source (Join-Path $artifactPath 'soplex-v8.0.2.zip') -Destination $sourceRoot -CopyName 'soplex-v8.0.2.zip'
Expand-ZipLike -Source (Join-Path $artifactPath 'pyscipopt-v6.2.1.zip') -Destination $sourceRoot -CopyName 'pyscipopt-v6.2.1.zip'

$pythonRoot = Join-Path $workPath 'python'
Expand-ZipLike -Source (Join-Path $artifactPath 'python.3.14.0.nupkg') -Destination $pythonRoot -CopyName 'python.3.14.0.zip'
$pythonExe = Join-Path $pythonRoot 'tools\python.exe'
$sitePackages = Join-Path $pythonRoot 'tools\Lib\site-packages'
foreach ($wheelName in @(
    'setuptools-83.0.0-py3-none-any.whl',
    'wheel-0.47.0-py3-none-any.whl',
    'cython-3.2.8-cp314-cp314-win_amd64.whl',
    'numpy-2.5.1-cp314-cp314-win_amd64.whl'
)) {
    $zipName = $wheelName.Replace('.whl', '.zip')
    Expand-ZipLike -Source (Join-Path $artifactPath $wheelName) -Destination $sitePackages -CopyName $zipName
}
Invoke-Checked -FilePath $pythonExe -ArgumentList @('-VV')

$soplexSource = Join-Path $sourceRoot 'soplex-8.0.2'
$soplexBuild = Join-Path $workPath 'soplex-build'
$soplexInstall = Join-Path $workPath 'soplex-install'
$soplexConfigure = @(
    '-S', $soplexSource,
    '-B', $soplexBuild,
    '-G', 'Visual Studio 17 2022',
    '-A', 'x64',
    '-T', 'v143,version=14.44',
    '-DCMAKE_SYSTEM_VERSION=10.0.26100.0',
    "-DCMAKE_INSTALL_PREFIX=$($soplexInstall.Replace('\', '/'))",
    '-DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreadedDLL',
    '-DBOOST=OFF', '-DGMP=OFF', '-DMPFR=OFF', '-DPAPILO=OFF',
    '-DQUADMATH=OFF', '-DZLIB=OFF', '-DMT=OFF'
)
Invoke-Checked -FilePath 'cmake' -ArgumentList $soplexConfigure
foreach ($target in @('libsoplexshared', 'soplex', 'libsoplex-pic')) {
    Invoke-Checked -FilePath 'cmake' -ArgumentList @('--build', $soplexBuild, '--config', 'Release', '--target', $target, '--parallel', '1')
}
Invoke-Checked -FilePath 'cmake' -ArgumentList @('--install', $soplexBuild, '--config', 'Release')

$scipSource = Join-Path $sourceRoot 'scip-10.0.2'
$scipBuild = Join-Path $workPath 'scip-build'
$scipInstall = Join-Path $workPath 'scip-install'
$soplexConfig = Join-Path $soplexInstall 'lib\cmake\soplex'
$scipConfigure = @(
    '-S', $scipSource,
    '-B', $scipBuild,
    '-G', 'Visual Studio 17 2022',
    '-A', 'x64',
    '-T', 'v143,version=14.44',
    '-DCMAKE_SYSTEM_VERSION=10.0.26100.0',
    "-DCMAKE_INSTALL_PREFIX=$($scipInstall.Replace('\', '/'))",
    '-DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreadedDLL',
    "-DSOPLEX_DIR=$($soplexConfig.Replace('\', '/'))",
    '-DAMPL=OFF', '-DAUTOBUILD=OFF', '-DCONOPT=OFF', '-DEXACTSOLVE=OFF',
    '-DEXPRINT=none', '-DGMP=OFF', '-DIPOPT=OFF', '-DLAPACK=OFF',
    '-DLPS=spx', '-DLPSEXACT=none', '-DLPSCHECK=OFF', '-DLTO=ON',
    '-DMPFR=OFF', '-DPAPILO=OFF', '-DREADLINE=OFF', '-DSHARED=ON',
    '-DSYM=snauty', '-DTPI=none', '-DWORHP=OFF', '-DZIMPL=OFF', '-DZLIB=OFF'
)
Invoke-Checked -FilePath 'cmake' -ArgumentList $scipConfigure
Invoke-Checked -FilePath 'cmake' -ArgumentList @('--build', $scipBuild, '--config', 'Release', '--target', 'libscip', '--parallel', '1')
Invoke-Checked -FilePath 'cmake' -ArgumentList @('--build', $scipBuild, '--config', 'Release', '--target', 'scip', '--parallel', '1')
Invoke-Checked -FilePath 'cmake' -ArgumentList @('--install', $scipBuild, '--config', 'Release')

$pyscipoptSource = Join-Path $sourceRoot 'PySCIPOpt-6.2.1'
$distRoot = Join-Path $workPath 'dist'
$tempRoot = Join-Path $workPath 'temp'
New-Item -ItemType Directory -Path $distRoot, $tempRoot -Force | Out-Null
$previousScipOptDir = $env:SCIPOPTDIR
$previousRelease = $env:RELEASE
$previousTemp = $env:TEMP
$previousTmp = $env:TMP
$previousPath = $env:PATH
try {
    $env:SCIPOPTDIR = $scipInstall
    $env:RELEASE = 'true'
    $env:TEMP = $tempRoot
    $env:TMP = $tempRoot
    $env:PATH = "$scipInstall\bin;$soplexInstall\bin;$previousPath"
    Push-Location $pyscipoptSource
    try {
        Invoke-Checked -FilePath $pythonExe -ArgumentList @('setup.py', 'bdist_wheel', '--dist-dir', $distRoot)
    } finally {
        Pop-Location
    }
} finally {
    $env:SCIPOPTDIR = $previousScipOptDir
    $env:RELEASE = $previousRelease
    $env:TEMP = $previousTemp
    $env:TMP = $previousTmp
    $env:PATH = $previousPath
}
$builtWheels = @(Get-ChildItem -LiteralPath $distRoot -Filter 'pyscipopt-6.2.1-cp314-cp314-win_amd64.whl')
if ($builtWheels.Count -ne 1) {
    throw 'Expected exactly one locally built PySCIPOpt cp314 wheel.'
}

$runtimeRoot = Join-Path $workPath 'runtime'
$runtimeSitePackages = Join-Path $runtimeRoot 'site-packages'
New-Item -ItemType Directory -Path $runtimeSitePackages -Force | Out-Null
Expand-ZipLike -Source (Join-Path $artifactPath 'numpy-2.5.1-cp314-cp314-win_amd64.whl') -Destination $runtimeSitePackages -CopyName 'runtime-numpy-2.5.1.zip'
Expand-ZipLike -Source $builtWheels[0].FullName -Destination $runtimeSitePackages -CopyName 'runtime-pyscipopt-6.2.1.zip'
$pyscipoptRuntime = Join-Path $runtimeSitePackages 'pyscipopt'
Copy-Item -LiteralPath (Join-Path $scipInstall 'bin\libscip.dll') -Destination (Join-Path $pyscipoptRuntime 'libscip.dll') -Force
foreach ($name in @('msvcp140.dll', 'vcruntime140.dll', 'vcruntime140_1.dll')) {
    Copy-Item -LiteralPath (Join-Path $redistPath $name) -Destination (Join-Path $pyscipoptRuntime $name) -Force
}
$numpyPrivateMsvcp = @(Get-ChildItem -LiteralPath (Join-Path $runtimeSitePackages 'numpy.libs') -Filter 'msvcp140-*.dll')
if ($numpyPrivateMsvcp.Count -ne 1) {
    throw 'Expected exactly one NumPy-private msvcp140 DLL.'
}
Copy-Item -LiteralPath (Join-Path $redistPath 'msvcp140.dll') -Destination $numpyPrivateMsvcp[0].FullName -Force

$noticeRoot = Join-Path $runtimeRoot 'notices'
New-Item -ItemType Directory -Path $noticeRoot -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $pyscipoptSource 'LICENSE') -Destination (Join-Path $noticeRoot 'PySCIPOpt-MIT.txt') -Force
Copy-Item -LiteralPath (Join-Path $scipInstall 'share\licenses\scip') -Destination (Join-Path $noticeRoot 'SCIP') -Recurse -Force
Copy-Item -LiteralPath (Join-Path $soplexInstall 'share\licenses\soplex') -Destination (Join-Path $noticeRoot 'SoPlex') -Recurse -Force
Copy-Item -LiteralPath (Join-Path $runtimeSitePackages 'numpy-2.5.1.dist-info\licenses') -Destination (Join-Path $noticeRoot 'NumPy') -Recurse -Force
$noticeText = @"
Microsoft Visual C++ Runtime notice

Runtime family: Microsoft Visual C++ Redistributable for Visual Studio 2022
Source directory: $redistPath
Files redistributed locally: msvcp140.dll, vcruntime140.dll, vcruntime140_1.dll
The NumPy-private msvcp140 filename contains the exact bytes of the official msvcp140.dll source above.
Official deployment and redistribution terms:
https://learn.microsoft.com/en-us/cpp/windows/deployment-in-visual-cpp?view=msvc-170
https://visualstudio.microsoft.com/license-terms/
"@
[IO.File]::WriteAllText((Join-Path $noticeRoot 'Microsoft-Visual-Cpp-Runtime.txt'), $noticeText, [Text.UTF8Encoding]::new($false))

$summary = [ordered]@{
    schema_version = 'bgig.minimal_scip_runtime_build_summary.v1'
    work_root = $workPath
    runtime_root = $runtimeRoot
    built_wheel = $builtWheels[0].FullName
    built_wheel_size_bytes = $builtWheels[0].Length
    built_wheel_sha256 = (Get-FileHash -LiteralPath $builtWheels[0].FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    configuration = 'Release'
    process_parallelism = 1
    global_install_count = 0
    holdout_read = $false
}
$summaryPath = Join-Path $workPath 'build-summary.json'
[IO.File]::WriteAllText($summaryPath, (($summary | ConvertTo-Json -Depth 5) + "`n"), [Text.UTF8Encoding]::new($false))
Write-Host "MINIMAL_SCIP_BUILD_OK wheel=$($summary.built_wheel_sha256) runtime=$runtimeRoot"