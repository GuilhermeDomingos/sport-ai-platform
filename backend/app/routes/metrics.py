from fastapi import APIRouter

from app.schemas.metrics_schema import MetricsCalculationResponse
from app.services.biomechanics_service import calculate_metrics


router = APIRouter()


@router.post(
    "/{video_id}/metrics/calculate",
    response_model=MetricsCalculationResponse,
)
def calculate_video_metrics(video_id: str) -> dict:
    return calculate_metrics(video_id)
