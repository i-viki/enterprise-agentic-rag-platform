# ==============================================================================
# Enterprise Agentic RAG Platform - Teardown Script
# ==============================================================================

Write-Host "==================================================" -ForegroundColor Yellow
Write-Host " Stopping Enterprise Agentic RAG Platform" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Yellow

# 1. Stop Telemetry Containers
Write-Host "`n[1/3] Stopping Telemetry Containers..." -ForegroundColor Cyan
docker compose -f infrastructure/telemetry/docker-compose.telemetry.yml down

# 2. Stop Storage Containers
Write-Host "`n[2/3] Stopping PostgreSQL & Redis Containers..." -ForegroundColor Cyan
docker compose down

# 3. Clean up any lingering port listeners on 8080, 8000, 5173
Write-Host "`n[3/3] Checking for active host port listeners..." -ForegroundColor Cyan
$ports = @(8080, 8000, 5173)
foreach ($p in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue
    if ($conns) {
        foreach ($c in $conns) {
            try {
                Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
                Write-Host "  -> Terminated process on port $p (PID: $($c.OwningProcess))"
            } catch {}
        }
    }
}

Write-Host "`n==================================================" -ForegroundColor Green
Write-Host " Platform is completely stopped and cleaned up." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

