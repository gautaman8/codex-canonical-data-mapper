CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS canonical_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    correlation_id UUID NOT NULL,
    event_type VARCHAR(80) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dicom_studies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_instance_uid VARCHAR(128) UNIQUE NOT NULL,
    patient_id VARCHAR(100),
    modality VARCHAR(50),
    study_date TIMESTAMPTZ,
    received_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,
    correlation_id UUID
);

CREATE TABLE IF NOT EXISTS processed_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION block_canonical_mutation()
RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'canonical_events is append-only and immutable';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS canonical_events_no_update ON canonical_events;
CREATE TRIGGER canonical_events_no_update
BEFORE UPDATE OR DELETE ON canonical_events
FOR EACH ROW EXECUTE FUNCTION block_canonical_mutation();
