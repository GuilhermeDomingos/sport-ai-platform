from enum import Enum

from pydantic import BaseModel, Field


class CameraView(str, Enum):
    FRONT = "front"
    SIDE = "side"


class DetectedCameraView(str, Enum):
    FRONT = "front"
    SIDE = "side"
    UNKNOWN = "unknown"


class CameraViewValidationStatus(str, Enum):
    VALID = "valid"
    MISMATCH = "mismatch"
    UNCERTAIN = "uncertain"


class CameraViewInferenceResult(BaseModel):
    detected_camera_view: DetectedCameraView
    confidence: int
    front_score: int
    side_score: int
    reasons: list[str] = Field(default_factory=list)


class CameraViewValidationResult(BaseModel):
    selected_camera_view: CameraView
    detected_camera_view: DetectedCameraView
    confidence: int
    status: CameraViewValidationStatus
    is_valid: bool
    should_block_analysis: bool
    message: str
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
