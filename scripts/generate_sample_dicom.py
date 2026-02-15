from pathlib import Path

from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid


def build_sample(path: Path) -> None:
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = generate_uid()
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.ImplementationClassUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = FileDataset(str(path), {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.PatientName = "POC^PATIENT"
    ds.PatientID = "PATIENT-001"
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SOPInstanceUID = generate_uid()
    ds.Modality = "CT"
    ds.StudyDate = "20260215"
    ds.Rows = 1
    ds.Columns = 1
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelRepresentation = 0
    ds.PixelData = b"\x00\x00"
    ds.save_as(path)


if __name__ == "__main__":
    output = Path("scripts/sample.dcm")
    build_sample(output)
    print(output)
