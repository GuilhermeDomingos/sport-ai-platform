import json
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.biomechanics import camera_view_validator
from app.modules.biomechanics.camera_view_validator import (
    calculate_front_view_likelihood,
    calculate_side_view_likelihood,
    extract_camera_view_features,
    infer_camera_view,
    validate_camera_view,
)
from app.schemas.camera_schema import (
    CameraView,
    CameraViewInferenceResult,
    CameraViewValidationStatus,
    DetectedCameraView,
)
from app.services import (
    biomechanics_service,
    camera_view_validation_service,
    scoring_service,
    video_service,
)


client = TestClient(app)


def _landmark(name: str, x: float, y: float, visibility: float = 0.95) -> dict:
    return {"name": name, "x": x, "y": y, "z": 0.0, "visibility": visibility}


def _front_frame() -> dict:
    return {
        "poseDetected": True,
        "landmarks": [
            _landmark("left_shoulder", 0.35, 0.20),
            _landmark("right_shoulder", 0.65, 0.20),
            _landmark("left_hip", 0.40, 0.45),
            _landmark("right_hip", 0.60, 0.45),
            _landmark("left_knee", 0.38, 0.65),
            _landmark("right_knee", 0.62, 0.65),
            _landmark("left_ankle", 0.36, 0.88),
            _landmark("right_ankle", 0.64, 0.88),
        ],
    }


def _side_frame() -> dict:
    return {
        "poseDetected": True,
        "landmarks": [
            _landmark("left_shoulder", 0.50, 0.20, 0.30),
            _landmark("right_shoulder", 0.55, 0.20, 0.95),
            _landmark("left_hip", 0.50, 0.45, 0.30),
            _landmark("right_hip", 0.54, 0.45, 0.95),
            _landmark("left_knee", 0.51, 0.65, 0.30),
            _landmark("right_knee", 0.54, 0.65, 0.95),
            _landmark("left_ankle", 0.52, 0.88, 0.30),
            _landmark("right_ankle", 0.54, 0.88, 0.95),
        ],
    }


def _frames(frame: dict, count: int = 12) -> list[dict]:
    return [frame for _ in range(count)]


def test_front_features_and_likelihood_score_front_view() -> None:
    features = extract_camera_view_features(_frames(_front_frame()))

    assert features.valid_frame_count == 12
    assert features.both_shoulders_visible
    assert features.avg_shoulder_width_ratio >= 0.16
    assert calculate_front_view_likelihood(features) > calculate_side_view_likelihood(features)


def test_side_features_and_likelihood_score_side_view() -> None:
    features = extract_camera_view_features(_frames(_side_frame()))

    assert features.valid_frame_count == 12
    assert not features.both_shoulders_visible
    assert features.left_right_confidence_diff >= 0.18
    assert calculate_side_view_likelihood(features) > calculate_front_view_likelihood(features)


def test_infer_camera_view_unknown_when_too_few_frames() -> None:
    inference = infer_camera_view(_frames(_front_frame(), count=4))

    assert inference.detected_camera_view is DetectedCameraView.UNKNOWN
    assert inference.confidence == 0


def test_infer_camera_view_unknown_when_score_difference_is_small(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(camera_view_validator, "calculate_front_view_likelihood", lambda _: 63)
    monkeypatch.setattr(camera_view_validator, "calculate_side_view_likelihood", lambda _: 58)

    inference = infer_camera_view(_frames(_front_frame()))

    assert inference.detected_camera_view is DetectedCameraView.UNKNOWN
    assert inference.confidence == 63


def test_validate_camera_view_blocks_strong_mismatch() -> None:
    validation = validate_camera_view(CameraView.SIDE, _frames(_front_frame()))

    assert validation.status is CameraViewValidationStatus.MISMATCH
    assert validation.should_block_analysis
    assert not validation.is_valid


def test_validate_camera_view_low_confidence_mismatch_is_uncertain(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        camera_view_validator,
        "infer_camera_view",
        lambda _: CameraViewInferenceResult(
            detected_camera_view=DetectedCameraView.FRONT,
            confidence=61,
            front_score=61,
            side_score=40,
            reasons=["Sinais fracos."],
        ),
    )

    validation = validate_camera_view(CameraView.SIDE, _frames(_front_frame()))

    assert validation.status is CameraViewValidationStatus.UNCERTAIN
    assert not validation.should_block_analysis


def test_validate_camera_view_accepts_matching_view() -> None:
    validation = validate_camera_view(CameraView.FRONT, _frames(_front_frame()))

    assert validation.status is CameraViewValidationStatus.VALID
    assert validation.is_valid
    assert not validation.should_block_analysis


@pytest.fixture
def isolated_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    uploads = tmp_path / "uploads"
    outputs = tmp_path / "outputs"
    uploads.mkdir()
    outputs.mkdir()
    monkeypatch.setattr(video_service, "UPLOAD_DIR", uploads)
    monkeypatch.setattr(video_service, "OUTPUT_DIR", outputs)
    monkeypatch.setattr(biomechanics_service, "OUTPUT_DIR", outputs)
    monkeypatch.setattr(scoring_service, "OUTPUT_DIR", outputs)
    monkeypatch.setattr(camera_view_validation_service, "OUTPUT_DIR", outputs)
    return uploads, outputs


def _stored_video(
    uploads: Path, outputs: Path, camera_view: str = "side"
) -> tuple[str, Path]:
    video_id = str(uuid4())
    (uploads / f"{video_id}.mp4").write_bytes(b"video")
    video_dir = outputs / video_id
    video_dir.mkdir(parents=True)
    (video_dir / "video.json").write_text(
        json.dumps(
            {
                "videoId": video_id,
                "exerciseType": "squat",
                "cameraView": camera_view,
            }
        ),
        encoding="utf-8",
    )
    return video_id, video_dir


def _write_pose(video_dir: Path, frames: list[dict]) -> None:
    pose_dir = video_dir / "pose"
    pose_dir.mkdir(parents=True)
    (pose_dir / "landmarks.json").write_text(
        json.dumps({"frames": frames}),
        encoding="utf-8",
    )


def test_metrics_calculation_returns_422_on_camera_view_mismatch(
    isolated_storage: tuple[Path, Path],
) -> None:
    uploads, outputs = isolated_storage
    video_id, video_dir = _stored_video(uploads, outputs, camera_view="side")
    _write_pose(video_dir, _frames(_front_frame()))

    response = client.post(f"/videos/{video_id}/metrics/calculate")

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "CAMERA_VIEW_MISMATCH"
    assert body["selected_camera_view"] == "side"
    assert body["detected_camera_view"] == "front"
    assert not (video_dir / "metrics" / "metrics.json").exists()


def test_score_calculation_returns_422_when_persisted_validation_is_mismatch(
    isolated_storage: tuple[Path, Path],
) -> None:
    uploads, outputs = isolated_storage
    video_id, video_dir = _stored_video(uploads, outputs, camera_view="side")
    validation = validate_camera_view(CameraView.SIDE, _frames(_front_frame()))
    validation_dir = video_dir / "camera_view_validation"
    validation_dir.mkdir()
    (validation_dir / "validation.json").write_text(
        json.dumps(validation.model_dump(mode="json")),
        encoding="utf-8",
    )

    metrics_dir = video_dir / "metrics"
    metrics_dir.mkdir()
    (metrics_dir / "metrics.json").write_text(
        json.dumps(
            {
                "videoId": video_id,
                "movement": "squat",
                "camera_view": "side",
                "metrics": {
                    "averageKneeAngle": 130.0,
                    "minKneeAngle": 90.0,
                    "averageHipAngle": 120.0,
                    "torsoInclination": 18.0,
                    "depthClassification": "parallel",
                    "symmetryScore": 90,
                    "stabilityScore": 90,
                },
            }
        ),
        encoding="utf-8",
    )
    movement_dir = video_dir / "movement"
    movement_dir.mkdir()
    (movement_dir / "movement_analysis.json").write_text(
        json.dumps(
            {
                "videoId": video_id,
                "movement": "squat",
                "camera_view": "side",
                "totalReps": 0,
                "reps": [],
            }
        ),
        encoding="utf-8",
    )

    response = client.post(f"/videos/{video_id}/score/calculate")

    assert response.status_code == 422
    assert response.json()["code"] == "CAMERA_VIEW_MISMATCH"
    assert not (video_dir / "score" / "scoring.json").exists()
