import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.models.events import DeviceEventIn, DicomWebhookIn, EventAck
from app.repositories.persistence import PersistenceRepository
from app.services.messaging import MessagingService
from app.services.orthanc import OrthancService

router = APIRouter()
logger = logging.getLogger(__name__)
persistence = PersistenceRepository()
messaging = MessagingService()
orthanc = OrthancService()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/v1/device-events", response_model=EventAck, status_code=status.HTTP_202_ACCEPTED)
def ingest_device_event(payload: DeviceEventIn) -> EventAck:
    idempotency_key = f"device:{payload.event_id}"
    inserted = persistence.register_idempotency_key(idempotency_key)
    if not inserted:
        return EventAck(status="accepted", correlation_id=payload.correlation_id, deduplicated=True)

    data = payload.model_dump(mode="json")
    persistence.persist_canonical_event(str(payload.correlation_id), "device", data)
    messaging.publish("device-events", payload.device_id, data)
    messaging.publish("canonical-data", payload.device_id, data)

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


@router.post("/v1/dicom/orthanc/sync", status_code=status.HTTP_202_ACCEPTED)
def sync_latest_study_from_orthanc(correlation_id: UUID) -> EventAck:
    try:
        studies = orthanc.list_studies()
        if not studies:
            raise HTTPException(status_code=404, detail="No studies available in Orthanc")

        metadata = orthanc.fetch_study_metadata(studies[-1])
        dicom_payload = DicomWebhookIn(correlation_id=correlation_id, **metadata)
        return ingest_dicom_metadata(dicom_payload)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("orthanc_sync_failed", extra={"correlation_id": str(correlation_id)})
        raise HTTPException(status_code=502, detail=f"Orthanc sync failed: {exc}") from exc
