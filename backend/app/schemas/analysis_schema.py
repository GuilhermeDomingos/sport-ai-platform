from pydantic import BaseModel

from app.schemas.camera_schema import CameraView
from app.schemas.feedback_schema import FeedbackResponse
from app.schemas.metrics_schema import SquatMetrics
from app.schemas.movement_schema import RepAnalysis
from app.schemas.processing_schema import VideoMetadata
from app.schemas.scoring_schema import ScoreBreakdown


class PersistedMetrics(BaseModel):
    videoId: str
    movement: str
    camera_view: CameraView | None = None
    metrics: SquatMetrics


class AnalysisResponse(BaseModel):
    videoId: str
    status: str
    movement: str
    camera_view: CameraView | None = None
    metadata: VideoMetadata
    metrics: SquatMetrics
    totalReps: int
    reps: list[RepAnalysis]
    score: ScoreBreakdown
    feedback: FeedbackResponse
