<#
.SYNOPSIS
Checks local tools needed for catalog refresh, manuscript checks, and PDF builds.

.DESCRIPTION
This script is intentionally PowerShell-native so Windows users can diagnose a
broken Python launcher before running the Python-based catalog scripts.
#>

$ErrorActionPreference = "Continue"

function Test-CommandRun {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name,
        [Parameter(Mandatory = $true)]
        [string[]] $Command
    )

    $executable = Get-Command $Command[0] -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $executable) {
        [pscustomobject]@{
            Tool = $Name
            Status = "missing"
            Command = ($Command -join " ")
            Detail = "Executable not found on PATH"
        }
        return
    }

    $output = & $Command[0] @($Command[1..($Command.Count - 1)]) 2>&1
    $exitCode = $LASTEXITCODE
    if ($null -eq $exitCode) {
        $exitCode = 0
    }

    [pscustomobject]@{
        Tool = $Name
        Status = $(if ($exitCode -eq 0) { "ok" } else { "failed" })
        Command = ($Command -join " ")
        Detail = (($output | Select-Object -First 3) -join " ").Trim()
    }
}

$checks = @(
    @{ Name = "Python"; Command = @("python", "--version") },
    @{ Name = "Python launcher"; Command = @("py", "-3", "--version") },
    @{ Name = "Git"; Command = @("git", "--version") },
    @{ Name = "latexmk"; Command = @("latexmk", "--version") },
    @{ Name = "pdflatex"; Command = @("pdflatex", "--version") }
)

$results = foreach ($check in $checks) {
    Test-CommandRun -Name $check.Name -Command $check.Command
}

$results | Format-Table -AutoSize

$pythonUsable = @($results | Where-Object {
    $_.Tool -in @("Python", "Python launcher") -and $_.Status -eq "ok"
}).Count -gt 0
$gitUsable = @($results | Where-Object {
    $_.Tool -eq "Git" -and $_.Status -eq "ok"
}).Count -gt 0

if (-not $pythonUsable -or -not $gitUsable) {
    Write-Host ""
    Write-Host "Required refresh prerequisites are unavailable. Install or repair Python/Git before running catalog generation." -ForegroundColor Yellow
    exit 1
}

exit 0
