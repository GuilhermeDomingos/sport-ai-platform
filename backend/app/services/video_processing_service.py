import cv2
from fastapi import HTTPException, status

from app.core.config import UPLOAD_DIR
from app.services.video_service import get_video_info


def process_video(video_id: str) -> dict:
    video_info = get_video_info(video_id)
    video_path = UPLOAD_DIR / video_info["filename"]

    if not video_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video nao encontrado.",
        )

    capture = cv2.VideoCapture(str(video_path))
    try:
        if not capture.isOpened():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nao foi possivel abrir o video para processamento.",
            )

        fps = capture.get(cv2.CAP_PROP_FPS)
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    finally:
        capture.release()

    duration_seconds = total_frames / fps if fps > 0 else 0
    file_size_mb = video_path.stat().st_size / (1024 * 1024)

    return {
        "videoId": video_id,
        "status": "processed",
        "metadata": {
            "durationSeconds": round(duration_seconds, 2),
            "fps": round(fps, 2),
            "totalFrames": total_frames,
            "resolution": {
                "width": width,
                "height": height,
            },
            "fileSizeMb": round(file_size_mb, 2),
        },
    }
