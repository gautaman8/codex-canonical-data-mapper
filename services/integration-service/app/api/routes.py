import logging

from fastapi import APIRouter, status

from app.models.events import DeviceEventIn, DicomWebhookIn, EventAck
from app.repositories.persistence import PersistenceRepository
from app.services.messaging import MessagingService

router = APIRouter()
logger = logging.getLogger(__name__)
persistence = PersistenceRepository()
messaging = MessagingService()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/v1/device-events", response_model=EventAck, status_code=status.HTTP_202_ACCEPTED)
def ingest_device_event(payload: DeviceEventIn) -> EventAck:
    idempotency_key = f"device:{payload.event_id}"
    inserted = persistence.register_idempotency_key(idempotency_key)
    if not inserted:
        return EventAck(status="accepted", correlation_id=payload.correlation_id, deduplicated=True)

    persistence.persist_canonical_event(str(payload.correlation_id), "device", payload.model_dump())
    messaging.publish("device-events", payload.device_id, payload.model_dump(mode="json"))
    messaging.publish("canonical-data", payload.device_id, payload.model_dump(mode="json"))

    logger.info(
        "device_event_ingested",
        extra={"correlation_id": str(payload.correlation_id), "device_id": payload.device_id},
    )
    return EventAck(status="accepted", correlation_id=payload.correlation_id)


@router.post("/v1/dicom/webhook", response_model=EventAck, status_code=status.HTTP_202_ACCEPTED)
def ingest_dicom_metadata(payload: DicomWebhookIn) -> EventAck:
    idempotency_key = f"dicom:{payload.study_instance_uid}"
    inserted = persistence.register_idempotency_key(idempotency_key)
    if not inserted:
        return EventAck(status="accepted", correlation_id=payload.correlation_id, deduplicated=True)

    data = payload.model_dump(mode="json")
    persistence.persist_dicom_study(data)
    persistence.persist_canonical_event(str(payload.correlation_id), "dicom", data)
    messaging.publish("dicom-events", payload.study_instance_uid, data)
    messaging.publish("canonical-data", payload.patient_id or "unknown", data)

    logger.info(
        "dicom_metadata_ingested",
        extra={
            "correlation_id": str(payload.correlation_id),
            "study_instance_uid": payload.study_instance_uid,
        },
    )
    return EventAck(status="accepted", correlation_id=payload.correlation_id)
