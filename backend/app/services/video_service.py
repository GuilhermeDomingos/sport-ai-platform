import json
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import (
    ALLOWED_CONTENT_TYPES,
    ALLOWED_EXTENSIONS,
    MAX_VIDEO_SIZE_BYTES,
    MAX_VIDEO_SIZE_MB,
    OUTPUT_DIR,
    UPLOAD_DIR,
)
from app.schemas.camera_schema import CameraView


CHUNK_SIZE_BYTES = 1024 * 1024
SUPPORTED_EXERCISES = {"squat"}


def validate_video_extension(filename: str | None) -> str:
    original_filename = (filename or "").replace("\\", "/").rsplit("/", 1)[-1]
    extension = Path(original_filename).suffix.lower().lstrip(".")
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Extensao de video nao permitida.",
        )
    return extension


def validate_video_content_type(content_type: str | None) -> None:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de arquivo nao permitido.",
        )


def _public_path(filename: str) -> str:
    return f"app/uploads/{filename}"


def validate_camera_view(camera_view: str | CameraView | None) -> CameraView:
    try:
        if camera_view is None:
            raise ValueError
        if isinstance(camera_view, CameraView):
            return camera_view
        return CameraView(str(camera_view))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cameraView is required and must be either 'front' or 'side'.",
        ) from exc


def validate_exercise_type(exercise_type: str | None) -> str:
    normalized = (exercise_type or "").strip().lower()
    if normalized not in SUPPORTED_EXERCISES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="exerciseType is required and must be 'squat'.",
        )
    return normalized


def _manifest_path(video_id: str) -> Path:
    return OUTPUT_DIR / video_id / "video.json"


def _save_video_manifest(
    video_id: str, exercise_type: str, camera_view: CameraView
) -> None:
    path = _manifest_path(video_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output:
        json.dump(
            {
                "videoId": video_id,
                "exerciseType": exercise_type,
                "cameraView": camera_view.value,
            },
            output,
            ensure_ascii=True,
            indent=2,
        )


def get_video_manifest(video_id: str) -> dict:
    path = _manifest_path(video_id)
    if not path.is_file():
        return {
            "videoId": video_id,
            "exerciseType": "squat",
            "cameraView": CameraView.FRONT.value,
        }

    try:
        with path.open("r", encoding="utf-8") as source:
            payload = json.load(source)
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Metadados do video invalidos.",
        ) from exc

    camera_view = validate_camera_view(payload.get("cameraView"))
    exercise_type = validate_exercise_type(payload.get("exerciseType", "squat"))
    return {
        "videoId": video_id,
        "exerciseType": exercise_type,
        "cameraView": camera_view.value,
    }


async def save_video(
    file: UploadFile,
    exercise_type: str = "squat",
    camera_view: str | CameraView | None = None,
) -> dict:
    extension = validate_video_extension(file.filename)
    validate_video_content_type(file.content_type)
    normalized_exercise = validate_exercise_type(exercise_type)
    normalized_camera_view = validate_camera_view(camera_view)

    video_id = str(uuid4())
    stored_filename = f"{video_id}.{extension}"
    destination = UPLOAD_DIR / stored_filename
    size = 0

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with destination.open("xb") as output:
            while chunk := await file.read(CHUNK_SIZE_BYTES):
                size += len(chunk)
                if size > MAX_VIDEO_SIZE_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"O video deve ter no maximo {MAX_VIDEO_SIZE_MB}MB.",
                    )
                output.write(chunk)
    except HTTPException:
        destination.unlink(missing_ok=True)
        raise
    except OSError as exc:
        destination.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Nao foi possivel salvar o video.",
        ) from exc
    finally:
        await file.close()

    _save_video_manifest(video_id, normalized_exercise, normalized_camera_view)

    return {
        "message": "V\u00eddeo recebido com sucesso",
        "videoId": video_id,
        "filename": stored_filename,
        "originalFilename": file.filename or "",
        "contentType": file.content_type or "",
        "size": size,
        "path": _public_path(stored_filename),
        "exerciseType": normalized_exercise,
        "cameraView": normalized_camera_view.value,
    }


def get_video_info(video_id: str) -> dict:
    try:
        normalized_id = str(UUID(video_id))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video nao encontrado.",
        ) from exc

    for extension in ALLOWED_EXTENSIONS:
        stored_filename = f"{normalized_id}.{extension}"
        if (UPLOAD_DIR / stored_filename).is_file():
            manifest = get_video_manifest(normalized_id)
            return {
                "videoId": normalized_id,
                "filename": stored_filename,
                "exists": True,
                "path": _public_path(stored_filename),
                "exerciseType": manifest["exerciseType"],
                "cameraView": manifest["cameraView"],
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Video nao encontrado.",
    )
