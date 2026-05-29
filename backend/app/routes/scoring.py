from fastapi import APIRouter

from app.schemas.scoring_schema import ScoringResponse
from app.services.scoring_service import calculate_score


router = APIRouter()


@router.post(
    "/{video_id}/score/calculate",
    response_model=ScoringResponse,
)
def calculate_video_score(video_id: str) -> dict:
    return calculate_score(video_id)
