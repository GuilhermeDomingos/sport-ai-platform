from fastapi import APIRouter

from app.schemas.pose_schema import PoseDetectionResponse
from app.services.pose_detection_service import detect_pose


router = APIRouter()


@router.post("/{video_id}/pose/detect", response_model=PoseDetectionResponse)
def detect_video_pose(video_id: str) -> dict:
    return detect_pose(video_id)
