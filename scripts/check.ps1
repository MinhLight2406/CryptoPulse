$ErrorActionPreference = "Continue"
$fail = 0

function Step($name, $cmd) {
  Write-Host "`n==> $name" -ForegroundColor Cyan
  Invoke-Expression $cmd
  if ($LASTEXITCODE -ne 0) { Write-Host "FAIL: $name" -ForegroundColor Red; $script:fail++ }
  else { Write-Host "OK: $name" -ForegroundColor Green }
}

Step "ruff check"          "ruff check ."
Step "ruff format --check" "ruff format --check ."
Step "pytest"              "pytest"

if (-not (Test-Path .env)) { Copy-Item .env.example .env }
Step "docker compose config" "docker compose -f infra/compose/docker-compose.yml --env-file .env config -q"

if ($fail -eq 0) { Write-Host "`nTat ca kiem tra deu dat." -ForegroundColor Green }
else { Write-Host "`n$fail buoc loi." -ForegroundColor Red; exit 1 }
