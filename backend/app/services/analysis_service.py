import json
from pathlib import Path
from typing import TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationError

from app.core.config import OUTPUT_DIR
from app.schemas.analysis_schema import AnalysisResponse, PersistedMetrics
from app.schemas.feedback_schema import FeedbackResponse
from app.schemas.movement_schema import MovementAnalysisResponse
from app.schemas.scoring_schema import ScoringResponse
from app.services.video_processing_service import process_video
from app.services.video_service import get_video_info


ModelType = TypeVar("ModelType", bound=BaseModel)

ANALYSIS_NOT_AVAILABLE = (
    "Analise completa nao disponivel. Conclua o pipeline ate a geracao de feedback."
)
INVALID_ANALYSIS_RESULT = "Resultado processado invalido."


def _load_artifact(path: Path, model: type[ModelType]) -> ModelType:
    if not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ANALYSIS_NOT_AVAILABLE,
        )

    try:
        with path.open("r", encoding="utf-8") as source:
            return model.model_validate(json.load(source))
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_ANALYSIS_RESULT,
        ) from exc


def _ensure_same_analysis(
    video_id: str,
    movement: str,
    artifacts: list[
        PersistedMetrics
        | MovementAnalysisResponse
        | ScoringResponse
        | FeedbackResponse
    ],
) -> None:
    if any(
        artifact.videoId != video_id or artifact.movement != movement
        for artifact in artifacts
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_ANALYSIS_RESULT,
        )


def get_analysis(video_id: str) -> dict:
    video_info = get_video_info(video_id)
    normalized_id = video_info["videoId"]
    base_dir = OUTPUT_DIR / normalized_id
    metrics = _load_artifact(
        base_dir / "metrics" / "metrics.json",
        PersistedMetrics,
    )
    movement = _load_artifact(
        base_dir / "movement" / "movement_analysis.json",
        MovementAnalysisResponse,
    )
    scoring = _load_artifact(
        base_dir / "score" / "scoring.json",
        ScoringResponse,
    )
    feedback = _load_artifact(
        base_dir / "feedback" / "feedback.json",
        FeedbackResponse,
    )
    artifacts = [metrics, movement, scoring, feedback]
    _ensure_same_analysis(normalized_id, movement.movement, artifacts)
    metadata = process_video(normalized_id)["metadata"]

    result = AnalysisResponse(
        videoId=normalized_id,
        status="completed",
        movement=movement.movement,
        camera_view=movement.camera_view or metrics.camera_view or video_info.get("cameraView"),
        camera_view_validation=(
            movement.camera_view_validation
            or metrics.camera_view_validation
            or scoring.camera_view_validation
        ),
        metadata=metadata,
        metrics=metrics.metrics,
        totalReps=movement.totalReps,
        reps=movement.reps,
        score=scoring.score,
        feedback=feedback,
    )
    return result.model_dump()
