# Kiem tra tron ven: replay -> ghi ClickHouse -> doi chieu Parquet, roi replay LAN HAI va kiem tra lai.
param(
  [string]$Start = "2024-12-01",
  [string]$End = "2024-12-02"
)
$group = "e2e-" + (Get-Date -Format "yyyyMMddHHmmss")
$fail = 0

function Run($label, [scriptblock]$cmd) {
  Write-Host "`n==> $label" -ForegroundColor Cyan
  & $cmd
  if ($LASTEXITCODE -ne 0) { Write-Host "FAIL: $label" -ForegroundColor Red; $script:fail++ }
}

Run "reset"                 { .\scripts\reset.ps1 }
Run "replay lan 1"          { python services/replayer/src/main.py --start $Start --end $End --max-speed }
Run "ingest lan 1"          { python services/ingestor/src/main.py --group $group --idle-exit 15 }
Run "verify lan 1"          { python tests/integration/verify_ingest.py --start $Start --end $End }
Run "replay lan 2"          { python services/replayer/src/main.py --start $Start --end $End --max-speed }
Run "ingest lan 2"          { python services/ingestor/src/main.py --group $group --idle-exit 15 }
Run "verify lan 2 (FINAL phai giong het lan 1)" { python tests/integration/verify_ingest.py --start $Start --end $End }

if ($fail -eq 0) { Write-Host "`nTAT CA DAT: replay hai lan cho cung mot ket qua." -ForegroundColor Green }
else { Write-Host "`n$fail buoc loi." -ForegroundColor Red; exit 1 }
