[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$statePath = Join-Path $repositoryRoot "tmp\local-composer-processes.json"

if (-not (Test-Path -LiteralPath $statePath)) {
    Write-Output "No BGIG Studio process state found."
    exit 0
}

$state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
foreach ($entry in @($state.api, $state.ui)) {
    $process = Get-Process -Id $entry.process_id -ErrorAction SilentlyContinue
    if ($process) {
        if ($process.ProcessName -notin @("python", "python3", "node")) {
            throw "Refusing to stop PID $($entry.process_id): unexpected process $($process.ProcessName)."
        }
        Stop-Process -Id $entry.process_id -Force
    }
}
Remove-Item -LiteralPath $statePath -Force
Write-Output "BGIG Studio processes stopped."
