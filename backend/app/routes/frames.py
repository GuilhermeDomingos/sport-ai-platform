from fastapi import APIRouter, Query

from app.schemas.frame_schema import FrameExtractionResponse
from app.services.frame_extraction_service import extract_frames


router = APIRouter()


@router.post("/{video_id}/frames/extract", response_model=FrameExtractionResponse)
def extract_video_frames(
    video_id: str,
    interval_seconds: float = Query(default=0.3),
) -> dict:
    return extract_frames(video_id, interval_seconds)
