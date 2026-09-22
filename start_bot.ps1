# KhatmSaz local runner for Windows PowerShell.
# Keep this window open while the local bot should be online.
# The loop recovers from an unexpected Python process exit; Ctrl+C stops it.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:PYTHONPATH = "src"

function Test-KhatmSazPostgres {
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $connect = $client.ConnectAsync("127.0.0.1", 55433)
        return $connect.Wait(1500) -and $client.Connected
    }
    catch {
        return $false
    }
    finally {
        $client.Dispose()
    }
}

function Start-KhatmSazPostgres {
    if (Test-KhatmSazPostgres) {
        Write-Host "PostgreSQL is ready on 127.0.0.1:55433."
        return
    }

    # First try the project's existing Docker container. A successful
    # in-container pg_isready is not enough: the host port must really open.
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        try {
            $container = docker ps -a --filter "name=^/khatmsaz-py-postgres$" --format "{{.Names}}" 2>$null
            if ($container -eq "khatmsaz-py-postgres") {
                Write-Host "Starting the KhatmSaz PostgreSQL container..."
                docker start khatmsaz-py-postgres 2>$null | Out-Null
                for ($attempt = 0; $attempt -lt 10 -and -not (Test-KhatmSazPostgres); $attempt++) {
                    Start-Sleep -Seconds 1
                }
            }
        }
        catch {
            Write-Warning "Docker PostgreSQL could not be started: $($_.Exception.Message)"
        }
    }

    if (Test-KhatmSazPostgres) {
        Write-Host "PostgreSQL is ready on 127.0.0.1:55433."
        return
    }

    # Recovery fallback created by the 2026-09-20 database-port incident.
    # It contains a restored copy of the Docker database and is independent
    # from Docker Desktop's sometimes-broken Windows port publishing.
    $pgCtl = "C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe"
    $pgData = Join-Path $env:TEMP "khatmsaz-pg18-test"
    $pgLog = Join-Path $env:TEMP "khatmsaz-pg18-test.log"
    if ((Test-Path $pgCtl) -and (Test-Path (Join-Path $pgData "PG_VERSION"))) {
        Write-Host "Starting the local KhatmSaz PostgreSQL recovery cluster..."
        & $pgCtl -D $pgData -l $pgLog -o "-p 55433 -h 127.0.0.1" start | Out-Null
        for ($attempt = 0; $attempt -lt 10 -and -not (Test-KhatmSazPostgres); $attempt++) {
            Start-Sleep -Seconds 1
        }
    }

    if (-not (Test-KhatmSazPostgres)) {
        throw "PostgreSQL is unavailable on 127.0.0.1:55433. The bot was not started. See docs/ai/DEBUGGING.md."
    }
    Write-Host "PostgreSQL is ready on 127.0.0.1:55433."
}

Start-KhatmSazPostgres

Write-Host "Applying any pending database migrations..."
& ".\.venv\Scripts\python.exe" -m alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    throw "Alembic migration failed. The bot was not started."
}

while ($true) {
    Write-Host "Starting KhatmSaz bot..."
    & ".\.venv\Scripts\python.exe" -m khatmsaz.bootstrap
    if ($LASTEXITCODE -eq 0) {
        Write-Host "KhatmSaz stopped normally."
        break
    }
    Write-Warning "KhatmSaz stopped unexpectedly (exit code $LASTEXITCODE). Restarting in 5 seconds..."
    Start-Sleep -Seconds 5
}
