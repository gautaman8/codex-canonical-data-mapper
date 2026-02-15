# Phase 0 Architecture Gate (Days 1-3)

## 1) Logical Architecture (L1 + L2)
- External traffic ingress: **GCP API Gateway** (mandatory in deployed env)
- Integration middleware: stateless API service (FastAPI on Cloud Run target)
- Idempotency and persistence: PostgreSQL
- Messaging backbone: Kafka (core), Pub/Sub (edge fan-out)
- Imaging ingress: Orthanc for DICOM metadata extraction
- Object storage: GCS for raw DICOM artifacts

## 2) Service Boundary Map
- `api-gateway`: auth, rate limiting, request routing
- `integration-service`: request validation, idempotency, canonical normalization
- `dicom-adapter`: Orthanc REST integration/webhooks
- `event-publisher`: Kafka producer abstraction
- `event-consumers` (future): downstream processors

## 3) Messaging Strategy Matrix
| Channel | Use cases | Non-use cases |
|---|---|---|
| Kafka | Canonical internal streams, replay, ordering by partition key | External public callback delivery |
| Pub/Sub | Optional external fan-out and async notifications | Core canonical state propagation |

## 4) Canonical Data Model v0.1
- Append-only immutable event log (`canonical_events`)
- Event envelope: correlation_id, event_type, payload, created_at
- DICOM metadata modeled separately (`dicom_studies`) and linked via correlation_id

## 5) Versioning / Deprecation
- URI-based versioning (`/v1/...`)
- Minimum one-version compatibility window
- RFC7807 errors mandatory

## 6) Security Boundary
- OAuth2/JWT at API Gateway (local placeholder)
- mTLS for service-to-service (Phase 2)
- PHI redaction strategy in logs
- Secrets managed via Secret Manager (local env vars placeholder)

## 7) Observability Plan
- Structured JSON logs
- Correlation ID required on every request/event
- Metrics target: p95 latency, DLQ count, Kafka lag
- Trace target: Gateway -> Service -> DB -> Kafka

## 8) DICOM Strategy (Orthanc)
- Orthanc receives/stores DICOM objects
- Middleware retrieves metadata only
- Raw DICOM never written to canonical DB
- Raw DICOM stored in GCS/object storage

## 9) DB Persistence Strategy
- Every accepted event persisted before Kafka publish
- Immutable canonical table with update/delete trigger blocks
- Idempotency table ensures duplicate suppression

## 10) API Gateway Architecture Design
- Single ingress to all public APIs
- Path-based routing to versioned backend services
- JWT authn + quota + request/response logging

## Architecture Verification Summary
This scaffold aligns with all non-negotiables through the POC boundary.
