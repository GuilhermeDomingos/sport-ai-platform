from pydantic import BaseModel

from app.schemas.camera_schema import CameraView, CameraViewValidationResult


class SquatMetrics(BaseModel):
    averageKneeAngle: float
    minKneeAngle: float
    averageHipAngle: float
    torsoInclination: float
    depthClassification: str
    symmetryScore: int
    stabilityScore: int
    cameraView: CameraView | None = None
    visibleSide: str | None = None
    squat_depth_ratio: float | None = None
    min_hip_angle: float | None = None
    max_knee_angle: float | None = None
    max_hip_angle: float | None = None
    knee_rom: float | None = None
    hip_rom: float | None = None
    hip_vertical_displacement: float | None = None
    range_of_motion: float | None = None
    max_trunk_inclination: float | None = None
    bottom_trunk_inclination: float | None = None
    trunk_variation: float | None = None
    movement_smoothness: int | None = None
    bottom_control: int | None = None
    valid_pose_frame_ratio: float | None = None
    visible_side_landmark_confidence: float | None = None
    critical_landmarks_visible_ratio: float | None = None


class MetricsCalculationResponse(BaseModel):
    videoId: str
    status: str
    movement: str
    camera_view: CameraView | None = None
    camera_view_validation: CameraViewValidationResult | None = None
    metrics: SquatMetrics
