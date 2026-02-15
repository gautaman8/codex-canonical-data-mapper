from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx

from app.core.config import settings


class OrthancService:
    def __init__(self) -> None:
        self.base_url = settings.orthanc_base_url.rstrip("/")
        self.auth = (settings.orthanc_username, settings.orthanc_password)

    def list_studies(self) -> list[str]:
        response = httpx.get(f"{self.base_url}/studies", auth=self.auth, timeout=10)
        response.raise_for_status()
        return response.json()

    def fetch_study_metadata(self, orthanc_study_id: str) -> dict[str, Any]:
        response = httpx.get(f"{self.base_url}/studies/{orthanc_study_id}", auth=self.auth, timeout=10)
        response.raise_for_status()
        data = response.json()

        tags = data.get("MainDicomTags", {})
        study_date_raw = tags.get("StudyDate")
        study_date = None
        if study_date_raw:
            try:
                study_date = datetime.strptime(study_date_raw, "%Y%m%d").isoformat() + "Z"
            except ValueError:
                study_date = None

        return {
            "study_instance_uid": tags.get("StudyInstanceUID", orthanc_study_id),
            "patient_id": tags.get("PatientID"),
            "modality": tags.get("ModalitiesInStudy"),
            "study_date": study_date,
            "metadata": {
                "orthanc_id": orthanc_study_id,
                "main_dicom_tags": tags,
                "series": data.get("Series", []),
            },
        }
