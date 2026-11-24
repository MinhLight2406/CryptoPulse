# Xoa sach topic candles va bang candles de chay lai tu dau.
# Dung mat khau mac dinh trong .env.example; sua neu ban da doi.
$compose = @("compose", "-f", "infra/compose/docker-compose.yml", "--env-file", ".env")
$user = "cryptopulse"
$pass = "change_me"

docker @compose exec -T redpanda rpk topic delete candles
docker @compose exec -T redpanda rpk topic create candles -p 1 -r 1
docker @compose exec -T clickhouse clickhouse-client --user $user --password $pass --query "TRUNCATE TABLE IF EXISTS cryptopulse.candles"
Write-Host "Da reset topic candles va bang candles." -ForegroundColor Green
