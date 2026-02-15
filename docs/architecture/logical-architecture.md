# Logical Architecture (L1/L2)

```mermaid
flowchart LR
  A[Device / DICOM Source] --> B[GCP API Gateway]
  B --> C[Integration Service]
  C --> D[Idempotency Layer]
  D --> E[(PostgreSQL Canonical DB)]
  E --> F[Kafka Topics]
  C --> G[Orthanc]
  G --> H[(Object Storage/GCS for Raw DICOM)]
```

## Topic strategy
- `device-events` partition key: `device_id`
- `dicom-events` partition key: `study_instance_uid`
- `canonical-data` partition key: `patient_id`
- `dlq` partition key: `correlation_id`
