from typing import Any

from pydantic import BaseModel, Field

from app.schemas.camera_schema import CameraView, CameraViewValidationResult


class ScoringInput(BaseModel):
    analysis_id: str
    exercise_type: str
    camera_view: CameraView = CameraView.FRONT
    camera_view_validation: CameraViewValidationResult | None = None
    metrics: dict[str, Any]
    reps: list[dict[str, Any]] = Field(default_factory=list)
    pose_quality: dict[str, Any] | None = None


class ScoreDetail(BaseModel):
    metric: str
    value: Any | None = None
    status: str
    message: str


class ScoreComponent(BaseModel):
    name: str
    score: int
    weight: float
    status: str
    details: list[ScoreDetail] = Field(default_factory=list)


class ScoreResult(BaseModel):
    final_score: int | None
    movement_quality_score: int | None
    analysis_confidence: int
    classification: str
    summary: str
    components: list[ScoreComponent]
    warnings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    score_method: str
    score_type: str | None = None
    score_version: str
    sub_scores: dict[str, int] = Field(default_factory=dict)
