from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.video_schema import VideoInfoResponse, VideoUploadResponse
from app.services.video_service import get_video_info, save_video


router = APIRouter()


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    exerciseType: str = Form("squat"),
    cameraView: str | None = Form(None),
) -> dict:
    return await save_video(
        file,
        exercise_type=exerciseType,
        camera_view=cameraView,
    )


@router.get("/{video_id}", response_model=VideoInfoResponse)
def get_video(video_id: str) -> dict:
    return get_video_info(video_id)
