from fastapi import APIRouter

from app.schemas.analysis_schema import AnalysisResponse
from app.services.analysis_service import get_analysis


router = APIRouter()


@router.get("/{video_id}/analysis", response_model=AnalysisResponse)
def get_analysis_result(video_id: str) -> dict:
    return get_analysis(video_id)
