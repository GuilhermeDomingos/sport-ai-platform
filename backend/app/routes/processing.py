from fastapi import APIRouter

from app.schemas.processing_schema import VideoProcessingResponse
from app.services.video_processing_service import process_video


router = APIRouter()


@router.post("/{video_id}/process", response_model=VideoProcessingResponse)
def process(video_id: str) -> dict:
    return process_video(video_id)
