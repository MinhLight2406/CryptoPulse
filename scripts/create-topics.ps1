# Topic names must match libs/cryptopulse_common/topics.py
$topics = "trades", "features", "predictions", "labels", "drift-events", "model-events"
$compose = "docker compose -f infra/compose/docker-compose.yml --env-file .env"

foreach ($t in $topics) {
  Invoke-Expression "$compose exec -T redpanda rpk topic create $t -p 1 -r 1"
}
Invoke-Expression "$compose exec -T redpanda rpk topic list"
