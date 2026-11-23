$fail = 0

function Check($name, $url) {
  try {
    $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
    Write-Host "OK   $name ($($r.StatusCode))" -ForegroundColor Green
  } catch {
    Write-Host "FAIL $name ($url)" -ForegroundColor Red
    $script:fail++
  }
}

Check "Redpanda Console" "http://localhost:8080"
Check "MLflow"           "http://localhost:5000"
Check "ClickHouse"       "http://localhost:8123/ping"

$pong = docker compose -f infra/compose/docker-compose.yml --env-file .env exec -T redis redis-cli ping 2>$null
if ($pong -match "PONG") { Write-Host "OK   Redis" -ForegroundColor Green }
else { Write-Host "FAIL Redis" -ForegroundColor Red; $fail++ }

if ($fail -gt 0) { exit 1 }
