from pydantic import BaseModel

from app.schemas.camera_schema import CameraView, CameraViewValidationResult


class RepAnalysis(BaseModel):
    rep: int
    startFrame: int
    bottomFrame: int
    endFrame: int
    depth: str
    minKneeAngle: float
    stabilityScore: int
    symmetryScore: int | None = None
    durationFrames: int
    averageVelocity: float
    bottomTrunkInclination: float | None = None
    minHipAngle: float | None = None


class MovementAnalysisResponse(BaseModel):
    videoId: str
    movement: str
    camera_view: CameraView | None = None
    camera_view_validation: CameraViewValidationResult | None = None
    visibleSide: str | None = None
    totalReps: int
    reps: list[RepAnalysis]
