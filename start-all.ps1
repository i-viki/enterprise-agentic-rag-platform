# ==============================================================================
# Enterprise Agentic RAG Platform - Launch Script
# ==============================================================================

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Launching Enterprise Agentic RAG Platform" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Start Storage Containers (PostgreSQL 16 + Redis 7)
Write-Host "`n[1/5] Starting PostgreSQL 16 (pgvector) & Redis 7..." -ForegroundColor Yellow
docker compose up -d

# 2. Start Telemetry Containers (Jaeger, Prometheus, Grafana, Langfuse, OTel)
Write-Host "`n[2/5] Starting Telemetry Stack (Jaeger, Prometheus, Grafana, Langfuse)..." -ForegroundColor Yellow
docker compose -f infrastructure/telemetry/docker-compose.telemetry.yml up -d

# 3. Launch Python 3.12 FastAPI Cognitive Engine (Port 8000)
Write-Host "`n[3/5] Launching Python 3.12 FastAPI Engine on Port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot/services/memory-service'; .venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

# 4. Launch Java 21 Spring Boot Governance Gateway (Port 8080)
Write-Host "`n[4/5] Launching Java 21 Spring Boot Gateway on Port 8080..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot/services/core-api'; mvn spring-boot:run"

# 5. Launch React 18 Frontend Studio (Port 5173)
Write-Host "`n[5/5] Launching React 18 Studio on Port 5173..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot/frontend'; npm run dev"

Write-Host "`n==================================================" -ForegroundColor Green
Write-Host " Platform successfully initiated!" -ForegroundColor Green
Write-Host " React Studio:  http://localhost:5173" -ForegroundColor Green
Write-Host " Langfuse UI:   http://localhost:3100" -ForegroundColor Green
Write-Host " Grafana Hub:   http://localhost:3000" -ForegroundColor Green
Write-Host " Jaeger APM:    http://localhost:16686" -ForegroundColor Green
Write-Host " Prometheus:    http://localhost:9090" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

