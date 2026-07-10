[CmdletBinding()]
param(
    [int]$ApiPort = 8001,
    [int]$UiPort = 5173
)

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$statePath = Join-Path $repositoryRoot "tmp\local-composer-processes.json"
$node = (Get-Command node -ErrorAction Stop).Source
$python = (Get-Command python -ErrorAction Stop).Source
$viteCli = Join-Path $repositoryRoot "frontend\node_modules\vite\bin\vite.js"

if (-not (Test-Path -LiteralPath $viteCli)) {
    throw "Frontend dependencies are missing. Run npm install in frontend first."
}

if (Test-Path -LiteralPath $statePath) {
    throw "A previous local composer state exists. Run scripts\stop_local_composer.ps1 first."
}

foreach ($port in @($ApiPort, $UiPort)) {
    $listener = netstat -ano -p tcp | Select-String -Pattern "^\s*TCP\s+127\.0\.0\.1:$port\s+.*LISTENING\s+\d+\s*$" | Select-Object -First 1
    if ($listener) {
        throw "Port $port is already in use. Stop the owning process before starting BGIG Studio."
    }
}

$env:PYTHONPATH = Join-Path $repositoryRoot "src"
$api = Start-Process -FilePath $python -ArgumentList "-m", "board_game_insert_generator.local_composer", "--host", "127.0.0.1", "--port", $ApiPort -WorkingDirectory $repositoryRoot -WindowStyle Hidden -PassThru
$ui = Start-Process -FilePath $node -ArgumentList $viteCli, "--host", "127.0.0.1", "--port", $UiPort, "--strictPort" -WorkingDirectory (Join-Path $repositoryRoot "frontend") -WindowStyle Hidden -PassThru

$state = [ordered]@{
    api = [ordered]@{ process_id = $api.Id; port = $ApiPort }
    ui = [ordered]@{ process_id = $ui.Id; port = $UiPort }
}
[IO.File]::WriteAllText($statePath, ($state | ConvertTo-Json), [Text.UTF8Encoding]::new($false))

function Wait-ForLocalUrl([string]$url, [int]$processId) {
    for ($attempt = 0; $attempt -lt 25; $attempt++) {
        if (-not (Get-Process -Id $processId -ErrorAction SilentlyContinue)) {
            throw "The process for $url stopped unexpectedly."
        }
        try {
            $response = Invoke-WebRequest -UseBasicParsing $url -TimeoutSec 1
            if ($response.StatusCode -eq 200) { return }
        } catch {}
        Start-Sleep -Milliseconds 200
    }
    throw "BGIG Studio did not become available at $url."
}

try {
    Wait-ForLocalUrl "http://127.0.0.1:$ApiPort/api/health" $api.Id
    Wait-ForLocalUrl "http://127.0.0.1:$UiPort" $ui.Id
} catch {
    & (Join-Path $PSScriptRoot "stop_local_composer.ps1")
    throw
}

Write-Output "BGIG Studio is ready: http://127.0.0.1:$UiPort"
