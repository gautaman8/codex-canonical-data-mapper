# rms-integration

Local-first middleware scaffolding for the healthcare integration platform.

## Scope covered in this setup
- Phase 0 Architecture Gate artifacts (ADR template, architecture docs, risk/security/observability plans)
- Phase 1 POC scaffolding (FastAPI integration service, PostgreSQL schema, Kafka topic model, Orthanc local environment)
- Contract-first baseline (OpenAPI + schema definitions)
- Messaging-backbone-first structure (Kafka-centric, Pub/Sub placeholder)

## Repository layout
- `services/integration-service/` FastAPI middleware service skeleton
- `contracts/openapi/` API contracts (versioned)
- `contracts/schemas/` canonical schemas for events
- `postgres/` immutable canonical persistence SQL
- `infrastructure/local/` local docker-compose for Kafka/Postgres/Orthanc
- `docs/architecture/` architecture plans and verification checklist
- `docs/adr/` architecture decision records

## Quick start (local)
1. `docker compose -f infrastructure/local/docker-compose.yml up -d`
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r services/integration-service/requirements.txt`
4. `uvicorn app.main:app --app-dir services/integration-service --reload --port 8080`

## POC endpoints
- `POST /v1/device-events`
- `POST /v1/dicom/webhook`
- `GET /health`

## Notes
- Raw DICOM is designed to be stored in object storage only (GCS in target architecture; local placeholder in code).
- Canonical table is immutable with append-only enforcement trigger.
- All ingress is expected via API Gateway in deployed environments; local mode calls service directly for development only.
