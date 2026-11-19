<#
.SYNOPSIS
    Build and start Git Pizza MxDev Lite locally with the given simulation constants.

.DESCRIPTION
    Windows PowerShell 5.1, run from the repository root (deliverables.md section 6.1):

        RUN/start.ps1 -SpeedFactor 10 -ResetOnStartup $true

    Builds the project with MxBuild 11.16.1 and starts the Mendix 11.16.1 runtime through
    mxcli ("mxcli run --local"), on the runtime's built-in HSQLDB database, so no database
    server and no Docker are needed. The two constants are passed for this run only
    (mxcli --constant, which never writes to the project), so the model is not changed.
    Returns once the app answers HTTP at its base URL, prints that URL and exits 0;
    exits 1 with a message when the app cannot be built or started.

    Prerequisites: a JDK 21 (java on PATH or JAVA_HOME) and internet access on the first
    run (mxcli, MxBuild and the runtime are downloaded once and cached under %USERPROFILE%\.mxcli).

.PARAMETER SpeedFactor
    Simulation.SpeedFactor. Valid values are 1, 2, 5 and 10; any other value is passed on
    unchanged and the app falls back to 1 with a WARN line (lite-configuration.md section 1).

.PARAMETER ResetOnStartup
    Simulation.ResetOnStartup: $true or $false (also accepts true/false/1/0 as text).

.PARAMETER Port
    HTTP port of the app (default 8080).
#>
[CmdletBinding()]
param(
    [string]$SpeedFactor = '1',
    [string]$ResetOnStartup = 'false',
    [int]$Port = 8080
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

function Fail([string]$Message) {
    [Console]::Error.WriteLine("start.ps1: $Message")
    exit 1
}

# -ResetOnStartup arrives as text when the script is called with powershell -File.
switch -Regex ($ResetOnStartup.Trim()) {
    '^\$?(true|1|yes)$'  { $reset = 'true' }
    '^\$?(false|0|no)$'  { $reset = 'false' }
    default              { Fail "-ResetOnStartup must be `$true or `$false, not '$ResetOnStartup'" }
}

$root = Split-Path -Parent $PSScriptRoot
$mpr = Join-Path $root 'GitPizza.mpr'
if (-not (Test-Path $mpr)) { Fail "GitPizza.mpr not found in $root" }
Set-Location $root

# ---- mxcli: $env:MXCLI, mxcli.exe in the repository, on PATH, or downloaded once
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
    $dir = Join-Path $root '.mxcli-bin'
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $mxcli = Join-Path $dir 'mxcli.exe'
    $url = 'https://github.com/mendixlabs/mxcli/releases/download/nightly/mxcli-windows-amd64.exe'
    Write-Host "Downloading mxcli from $url"
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $mxcli
    } catch {
        Fail "could not download mxcli: $($_.Exception.Message). Put mxcli.exe in the repository root or set MXCLI."
    }
}

# ---- Java 21
$java = $null
if ($env:JAVA_HOME -and (Test-Path (Join-Path $env:JAVA_HOME 'bin\java.exe'))) { $java = Join-Path $env:JAVA_HOME 'bin\java.exe' }
if (-not $java) {
    $j = Get-Command 'java.exe' -ErrorAction SilentlyContinue
    if ($j) { $java = $j.Source }
}
if (-not $java) { Fail 'no Java found: install a JDK 21 and put it on PATH or set JAVA_HOME' }

# Native tools write progress to stderr; that must not stop the script.
$ErrorActionPreference = 'Continue'

# ---- a previous run of this script is stopped first, so a second start is clean
& $mxcli run stop -p $mpr | Out-Host

# ---- MxBuild and the runtime (cached after the first run)
& $mxcli run --local --setup --db-type hsqldb -p $mpr | Out-Host
if ($LASTEXITCODE -ne 0) { Fail "preparing MxBuild and the runtime failed (exit $LASTEXITCODE)" }

# ---- build and start; --detach returns once the app serves
$baseUrl = "http://localhost:$Port"
& $mxcli run --local --detach --db-type hsqldb -p $mpr --app-port $Port `
    --constant "Simulation.SpeedFactor=$SpeedFactor" `
    --constant "Simulation.ResetOnStartup=$reset" `
    --constant "Shop.AppUrl=$baseUrl/" | Out-Host
if ($LASTEXITCODE -ne 0) {
    Fail "the app could not be built or started (exit $LASTEXITCODE); see .mxcli\run.log and .mxcli\runtime.log"
}

# ---- confirm the base URL answers
$deadline = (Get-Date).AddMinutes(5)
$ok = $false
while ((Get-Date) -lt $deadline) {
    try {
        $r = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/" -TimeoutSec 10
        if ($r.StatusCode -eq 200) { $ok = $true; break }
    } catch { }
    Start-Sleep -Seconds 2
}
if (-not $ok) { Fail "the app did not answer at $baseUrl within 5 minutes; see .mxcli\runtime.log" }

Write-Output $baseUrl
exit 0
