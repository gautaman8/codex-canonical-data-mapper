# Risk Register (Initial)

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | Inconsistent idempotency keys from vendors | Duplicate processing | Normalize and enforce deterministic idempotency strategy in adapters |
| R2 | High-cardinality partition keys causing skew | Throughput bottleneck | Partition strategy review with load test before Phase 2 completion |
| R3 | Orthanc outage | Delayed DICOM metadata flow | Retry + buffering + replay queue in Phase 2 |
| R4 | PHI leakage in logs | Compliance breach | Structured logging with redaction filters before production |
| R5 | Contract drift between services and docs | Integration failures | Contract-first CI checks and schema registry compatibility rules |
