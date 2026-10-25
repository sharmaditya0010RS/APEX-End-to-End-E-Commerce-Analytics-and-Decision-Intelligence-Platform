$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Checks = @(
    @{Name="Git"; Command="git"; Arguments=@("--version")}
    @{Name="Python"; Command="py"; Arguments=@("-3.12","--version")}
    @{Name="Docker"; Command="docker"; Arguments=@("--version")}
    @{Name="Docker Compose"; Command="docker"; Arguments=@("compose","version")}
)

$Results = foreach ($Check in $Checks) {
    try {
        $Output = & $Check.Command @($Check.Arguments) 2>&1
        [pscustomobject]@{
            Check = $Check.Name
            Status = if ($LASTEXITCODE -eq 0) {"PASS"} else {"FAIL"}
            Details = ($Output | Out-String).Trim()
        }
    }
    catch {
        [pscustomobject]@{
            Check = $Check.Name
            Status = "FAIL"
            Details = $_.Exception.Message
        }
    }
}

$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (Test-Path $Python) {
    & $Python -c "import pandas, numpy, scipy, plotly, sklearn, sqlalchemy, psycopg; print('Python analytics imports passed')"
    $PythonPassed = $LASTEXITCODE -eq 0
}
else {
    $PythonPassed = $false
}

$Results += [pscustomobject]@{
    Check = "Python Environment"
    Status = if ($PythonPassed) {"PASS"} else {"FAIL"}
    Details = "Analytics package imports"
}

docker info --format "{{.ServerVersion}}" 2>$null | Out-Null
$EnginePassed = $LASTEXITCODE -eq 0

$Results += [pscustomobject]@{
    Check = "Docker Engine"
    Status = if ($EnginePassed) {"PASS"} else {"FAIL"}
    Details = "Docker engine connectivity"
}

if ($EnginePassed) {
    docker exec apex_postgres pg_isready -U apex_admin -d apex_warehouse 2>$null | Out-Null
    $DatabasePassed = $LASTEXITCODE -eq 0
}
else {
    $DatabasePassed = $false
}

$Results += [pscustomobject]@{
    Check = "PostgreSQL"
    Status = if ($DatabasePassed) {"PASS"} else {"FAIL"}
    Details = "Database readiness"
}

$Results | Format-Table -AutoSize

if ($Results.Status -contains "FAIL") {
    throw "Environment verification failed"
}

Write-Host "PHASE 0 AUTOMATED CHECKS PASSED" -ForegroundColor Green
