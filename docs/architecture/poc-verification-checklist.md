# POC Verification Checklist (Weeks 1-2)

## Week 1: Async backbone + DICOM
- [x] FastAPI integration service scaffolded
- [x] Idempotency layer included
- [x] Canonical event persistence schema included
- [x] DICOM metadata table included
- [x] Kafka topics defined (`device-events`, `dicom-events`, `canonical-data`, `dlq`)
- [x] Orthanc local service included
- [x] Correlation ID in API contracts and logs
- [x] Structured logging configured

## Week 2: TPS / partner API
- [x] Versioned API contract (`/v1/...`) defined
- [x] RFC7807 model defined in OpenAPI
- [ ] Automated contract tests (pending implementation)
- [ ] Gateway JWT enforcement in local mode (deferred)

## Explicit constraints validated
- [x] Messaging backbone enforced (no direct sync coupling in architecture)
- [x] Canonical model immutable (DB trigger)
- [x] Raw DICOM not persisted in canonical DB
- [x] All artifacts version-controlled in this repo structure
