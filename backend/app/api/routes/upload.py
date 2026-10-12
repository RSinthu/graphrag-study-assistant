"""POST /upload - run the LangChain ingestion pipeline on a file."""
import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.config import get_settings
from app.schemas.models import UploadResponse
from app.services.ingestion import SUPPORTED_EXTENSIONS, ingest_file

router = APIRouter(tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
def upload(file: UploadFile) -> UploadResponse:
    filename = Path(file.filename or "").name  # drop any client-side folders
    if Path(filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
        allowed = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {allowed}")

    upload_dir = get_settings().upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / filename
    with path.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    try:
        result = ingest_file(path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return UploadResponse(filename=filename, **result)
