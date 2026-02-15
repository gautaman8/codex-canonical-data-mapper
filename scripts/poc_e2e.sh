#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python -m venv .venv
source .venv/bin/activate
pip install -q -r services/integration-service/requirements.txt pydicom

docker compose -f infrastructure/local/docker-compose.yml up -d

for i in {1..30}; do
  if curl -sSf http://localhost:8042/system >/dev/null; then
    break
  fi
  sleep 2
done

python scripts/generate_sample_dicom.py
curl -sS -u orthanc:orthanc -X POST http://localhost:8042/instances --data-binary @scripts/sample.dcm >/tmp/orthanc_upload.json

uvicorn app.main:app --app-dir services/integration-service --port 8080 >/tmp/integration-service.log 2>&1 &
APP_PID=$!
trap 'kill ${APP_PID} >/dev/null 2>&1 || true' EXIT

for i in {1..30}; do
  if curl -sSf http://localhost:8080/health >/dev/null; then
    break
  fi
  sleep 1
done

CORR_ID="11111111-1111-1111-1111-111111111111"
curl -sS -X POST "http://localhost:8080/v1/dicom/orthanc/sync?correlation_id=${CORR_ID}" -H "Content-Type: application/json" >/tmp/sync_response.json
curl -sS -X POST http://localhost:8080/v1/device-events \
  -H "Content-Type: application/json" \
  -d '{"correlation_id":"22222222-2222-2222-2222-222222222222","event_id":"evt-1","device_id":"device-1","event_type":"telemetry","payload":{"temp":37.1},"occurred_at":"2026-02-15T00:00:00Z"}' >/tmp/device_response.json

DB_CONTAINER=$(docker compose -f infrastructure/local/docker-compose.yml ps -q postgres)
DB_ROWS=$(docker exec "$DB_CONTAINER" psql -U integration -d integration -t -c "select count(*) from canonical_events;")
DICOM_ROWS=$(docker exec "$DB_CONTAINER" psql -U integration -d integration -t -c "select count(*) from dicom_studies;")

printf "canonical_events=%s\n" "${DB_ROWS// /}"
printf "dicom_studies=%s\n" "${DICOM_ROWS// /}"

echo "POC e2e completed"
