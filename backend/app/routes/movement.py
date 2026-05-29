from fastapi import APIRouter

from app.schemas.movement_schema import MovementAnalysisResponse
from app.services.movement_analysis_service import analyze_movement


router = APIRouter()


@router.post(
    "/{video_id}/movement/analyze",
    response_model=MovementAnalysisResponse,
)
def analyze_video_movement(video_id: str) -> dict:
    return analyze_movement(video_id)
