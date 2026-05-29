from fastapi import APIRouter

from app.schemas.feedback_schema import FeedbackResponse
from app.services.feedback_service import generate_feedback


router = APIRouter()


@router.post(
    "/{video_id}/feedback/generate",
    response_model=FeedbackResponse,
)
def generate_video_feedback(video_id: str) -> dict:
    return generate_feedback(video_id)
