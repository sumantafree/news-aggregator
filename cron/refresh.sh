#!/bin/sh
set -e
: "${API_URL:?API_URL env var required}"
: "${CRON_SECRET:?CRON_SECRET env var required}"

echo "[cron] POST $API_URL/cron/refresh"
curl -fsS -X POST \
  -H "X-Cron-Secret: $CRON_SECRET" \
  "$API_URL/cron/refresh"
echo
