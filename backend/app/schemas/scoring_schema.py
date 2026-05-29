from typing import Any

from pydantic import BaseModel, Field

from app.schemas.camera_schema import CameraViewValidationResult


class ScoreDetailSchema(BaseModel):
    metric: str
    value: Any | None = None
    status: str
    message: str


class ScoreComponentSchema(BaseModel):
    name: str
    score: int
    weight: float
    status: str
    details: list[ScoreDetailSchema] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    overallScore: int | None
    depthScore: int
    stabilityScore: int
    symmetryScore: int
    consistencyScore: int
    final_score: int | None = None
    movement_quality_score: int | None = None
    analysis_confidence: int | None = None
    classification: str | None = None
    summary: str | None = None
    components: list[ScoreComponentSchema] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    score_method: str | None = None
    score_type: str | None = None
    score_version: str | None = None
    sub_scores: dict[str, int] = Field(default_factory=dict)


class ScoringResponse(BaseModel):
    videoId: str
    status: str
    movement: str
    camera_view: str | None = None
    camera_view_validation: CameraViewValidationResult | None = None
    score: ScoreBreakdown
