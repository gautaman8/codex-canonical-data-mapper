from dataclasses import dataclass

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import settings


@dataclass
class PersistenceRepository:
    engine: Engine = create_engine(settings.postgres_dsn, pool_pre_ping=True)

    def persist_canonical_event(self, correlation_id: str, event_type: str, payload: dict) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO canonical_events (correlation_id, event_type, payload)
                    VALUES (:correlation_id, :event_type, CAST(:payload AS jsonb))
                    """
                ),
                {
                    "correlation_id": correlation_id,
                    "event_type": event_type,
                    "payload": str(payload).replace("'", '"'),
                },
            )

    def persist_dicom_study(self, payload: dict) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO dicom_studies (
                        study_instance_uid,
                        patient_id,
                        modality,
                        study_date,
                        metadata,
                        correlation_id
                    ) VALUES (
                        :study_instance_uid,
                        :patient_id,
                        :modality,
                        :study_date,
                        CAST(:metadata AS jsonb),
                        :correlation_id
                    )
                    ON CONFLICT (study_instance_uid) DO UPDATE
                    SET metadata = EXCLUDED.metadata,
                        patient_id = EXCLUDED.patient_id,
                        modality = EXCLUDED.modality,
                        study_date = EXCLUDED.study_date,
                        correlation_id = EXCLUDED.correlation_id
                    """
                ),
                {
                    "study_instance_uid": payload["study_instance_uid"],
                    "patient_id": payload.get("patient_id"),
                    "modality": payload.get("modality"),
                    "study_date": payload.get("study_date"),
                    "metadata": str(payload.get("metadata", {})).replace("'", '"'),
                    "correlation_id": payload["correlation_id"],
                },
            )

    def register_idempotency_key(self, idempotency_key: str) -> bool:
        with self.engine.begin() as connection:
            result = connection.execute(
                text(
                    """
                    INSERT INTO processed_messages (idempotency_key)
                    VALUES (:idempotency_key)
                    ON CONFLICT (idempotency_key) DO NOTHING
                    RETURNING idempotency_key
                    """
                ),
                {"idempotency_key": idempotency_key},
            )
            return result.scalar_one_or_none() is not None
