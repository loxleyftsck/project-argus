# Start MLflow UI Server (Windows)
# Usage: .\start_mlflow.ps1

Write-Host "Starting MLflow UI..." -ForegroundColor Green
Write-Host "Access at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

mlflow ui --port 5000 --host 0.0.0.0
