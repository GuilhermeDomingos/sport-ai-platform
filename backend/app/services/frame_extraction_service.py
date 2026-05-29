import shutil
from pathlib import Path

import cv2
from fastapi import HTTPException, status

from app.core.config import OUTPUT_DIR, UPLOAD_DIR
from app.services.video_service import get_video_info


def prepare_frames_output_dir(video_id: str) -> Path:
    output_dir = OUTPUT_DIR / video_id / "frames"

    if output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _public_output_dir(video_id: str) -> str:
    return f"app/outputs/{video_id}/frames"


def extract_frames(video_id: str, interval_seconds: float = 0.1) -> dict:
    if interval_seconds <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O intervalo de extracao deve ser maior que zero.",
        )

    video_info = get_video_info(video_id)
    normalized_id = video_info["videoId"]
    video_path = UPLOAD_DIR / video_info["filename"]

    capture = cv2.VideoCapture(str(video_path))
    try:
        if not capture.isOpened():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nao foi possivel abrir o video para extracao de frames.",
            )

        fps = capture.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nao foi possivel identificar o FPS do video.",
            )

        frame_interval = max(1, int(fps * interval_seconds))
        output_dir = prepare_frames_output_dir(normalized_id)
        saved_frames: list[str] = []
        current_frame_index = 0

        while True:
            success, frame = capture.read()
            if not success:
                break

            if current_frame_index % frame_interval == 0:
                frame_filename = f"frame_{len(saved_frames) + 1:06d}.jpg"
                if not cv2.imwrite(str(output_dir / frame_filename), frame):
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Nao foi possivel salvar um frame extraido.",
                    )
                saved_frames.append(frame_filename)

            current_frame_index += 1
    finally:
        capture.release()

    return {
        "videoId": normalized_id,
        "status": "frames_extracted",
        "frameIntervalSeconds": interval_seconds,
        "totalFramesExtracted": len(saved_frames),
        "outputDir": _public_output_dir(normalized_id),
        "frames": saved_frames,
    }
