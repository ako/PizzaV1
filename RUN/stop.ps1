<#
.SYNOPSIS
    Stop Git Pizza MxDev Lite and everything RUN/start.ps1 started.

.DESCRIPTION
    Windows PowerShell 5.1, run from the repository root:

        RUN/stop.ps1

    Stops the Mendix runtime and the MxBuild build server that start.ps1 started through
    "mxcli run --local --detach" (mxcli keeps their process ids in .mxcli\run-state.json).
    No container or database server is started by start.ps1, so nothing else is left.
    The HSQLDB data under deployment\data is kept for the next start.
    Exits 0 when nothing is left running; 1 with a message otherwise.
#>
[CmdletBinding()]
param([int]$Port = 8080)

Set-StrictMode -Version 2.0
$root = Split-Path -Parent $PSScriptRoot
$mpr = Join-Path $root 'GitPizza.mpr'
Set-Location $root

$mxcli = $null
$candidates = @($env:MXCLI, (Join-Path $root 'mxcli.exe'), (Join-Path $root '.mxcli-bin\mxcli.exe'))
foreach ($c in $candidates) {
    if ($c -and (Test-Path $c)) { $mxcli = $c; break }
}
if (-not $mxcli) {
    $onPath = Get-Command 'mxcli.exe' -ErrorAction SilentlyContinue
    if ($onPath) { $mxcli = $onPath.Source }
}
if (-not $mxcli) {
    # start.ps1 never ran here (it downloads mxcli first), so nothing of it can be running.
    Write-Output 'stopped (mxcli not found: nothing was started)'
    exit 0
}

& $mxcli run stop -p $mpr | Out-Host
$code = $LASTEXITCODE

# Nothing may still answer on the app port.
$listening = $false
try {
    $client = New-Object System.Net.Sockets.TcpClient
    $async = $client.BeginConnect('127.0.0.1', $Port, $null, $null)
    if ($async.AsyncWaitHandle.WaitOne(1000) -and $client.Connected) { $listening = $true }
    $client.Close()
} catch { }

if ($code -ne 0 -or $listening) {
    [Console]::Error.WriteLine("stop.ps1: the app is still running (mxcli exit $code, port $Port open); see .mxcli\run-state.json")
    exit 1
}
Write-Output 'stopped'
exit 0
