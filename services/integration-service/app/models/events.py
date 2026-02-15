from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class DeviceEventIn(BaseModel):
    correlation_id: UUID
    event_id: str = Field(min_length=1)
    device_id: str = Field(min_length=1)
    event_type: str = Field(min_length=1)
    payload: dict[str, Any]
    occurred_at: datetime


class DicomWebhookIn(BaseModel):
    correlation_id: UUID
    study_instance_uid: str = Field(min_length=1)
    patient_id: str | None = None
    modality: str | None = None
    study_date: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EventAck(BaseModel):
    status: str
    correlation_id: UUID
    deduplicated: bool = False
