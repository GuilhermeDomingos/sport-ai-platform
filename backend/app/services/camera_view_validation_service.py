import json
from pathlib import Path

from fastapi import HTTPException, status

from app.core.config import OUTPUT_DIR
from app.modules.biomechanics.camera_view_validator import (
    camera_view_recommendations,
    validate_camera_view,
)
from app.schemas.camera_schema import (
    CameraView,
    CameraViewValidationResult,
    CameraViewValidationStatus,
)


class CameraViewMismatchError(Exception):
    def __init__(self, validation_result: CameraViewValidationResult):
        self.validation_result = validation_result


def validation_path(video_id: str) -> Path:
    return OUTPUT_DIR / video_id / "camera_view_validation" / "validation.json"


def load_camera_view_validation(video_id: str) -> CameraViewValidationResult | None:
    path = validation_path(video_id)
    if not path.is_file():
        return None

    try:
        with path.open("r", encoding="utf-8") as source:
            return CameraViewValidationResult.model_validate(json.load(source))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validacao de camera view invalida.",
        ) from exc


def save_camera_view_validation(
    video_id: str, validation: CameraViewValidationResult
) -> None:
    path = validation_path(video_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output:
        json.dump(validation.model_dump(mode="json"), output, ensure_ascii=True, indent=2)


def get_or_create_camera_view_validation(
    video_id: str,
    selected_camera_view: CameraView,
    pose_frames: list[dict],
) -> CameraViewValidationResult:
    validation = load_camera_view_validation(video_id)
    if validation is not None:
        return validation

    validation = validate_camera_view(selected_camera_view, pose_frames)
    save_camera_view_validation(video_id, validation)
    return validation


def ensure_camera_view_allowed(validation: CameraViewValidationResult) -> None:
    if validation.should_block_analysis:
        raise CameraViewMismatchError(validation)


def mismatch_error_payload(validation: CameraViewValidationResult) -> dict:
    return {
        "code": "CAMERA_VIEW_MISMATCH",
        "message": validation.message,
        "selected_camera_view": validation.selected_camera_view.value,
        "detected_camera_view": validation.detected_camera_view.value,
        "confidence": validation.confidence,
        "reasons": validation.reasons,
        "recommendations": camera_view_recommendations(
            validation.selected_camera_view, validation.detected_camera_view
        ),
    }


def camera_view_validation_score(validation: CameraViewValidationResult | None) -> int:
    if validation is None:
        return 100
    if validation.status is CameraViewValidationStatus.UNCERTAIN:
        return min(validation.confidence, 60)
    if validation.status is CameraViewValidationStatus.MISMATCH:
        return 0
    return validation.confidence
