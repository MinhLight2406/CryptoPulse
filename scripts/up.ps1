if (-not (Test-Path .env)) { Copy-Item .env.example .env }
docker compose -f infra/compose/docker-compose.yml --env-file .env up -d
docker compose -f infra/compose/docker-compose.yml --env-file .env ps
