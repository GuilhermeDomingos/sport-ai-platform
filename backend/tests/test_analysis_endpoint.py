import json
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.services import analysis_service, video_service


client = TestClient(app)


def _artifacts(video_id: str) -> dict[str, dict]:
    return {
        "metrics/metrics.json": {
            "videoId": video_id,
            "movement": "squat",
            "metrics": {
                "averageKneeAngle": 141.03,
                "minKneeAngle": 82.07,
                "averageHipAngle": 132.24,
                "torsoInclination": 2.34,
                "depthClassification": "parallel",
                "symmetryScore": 92,
                "stabilityScore": 80,
            },
        },
        "movement/movement_analysis.json": {
            "videoId": video_id,
            "movement": "squat",
            "totalReps": 1,
            "reps": [
                {
                    "rep": 1,
                    "startFrame": 4,
                    "bottomFrame": 9,
                    "endFrame": 12,
                    "depth": "parallel",
                    "minKneeAngle": 89.05,
                    "stabilityScore": 83,
                    "symmetryScore": 92,
                    "durationFrames": 8,
                    "averageVelocity": 20.52,
                }
            ],
        },
        "score/scoring.json": {
            "videoId": video_id,
            "status": "score_calculated",
            "movement": "squat",
            "score": {
                "overallScore": 79,
                "depthScore": 65,
                "stabilityScore": 83,
                "symmetryScore": 91,
                "consistencyScore": 81,
                "final_score": 79,
                "movement_quality_score": 77,
                "analysis_confidence": 91,
                "classification": "Bom padrao, com pequenos ajustes",
                "summary": "AXON Movement Score calculado por sub-scores.",
                "components": [
                    {
                        "name": "mobility",
                        "score": 72,
                        "weight": 0.2,
                        "status": "good",
                        "details": [],
                    },
                    {
                        "name": "analysis_confidence",
                        "score": 91,
                        "weight": 0.15,
                        "status": "reliable",
                        "details": [],
                    },
                ],
                "warnings": [],
                "recommendations": ["Observe o alinhamento dos joelhos."],
                "score_method": "AXON_MOVEMENT_SCORE",
                "score_version": "1.0.0",
                "sub_scores": {
                    "mobility": 72,
                    "analysis_confidence": 91,
                },
            },
        },
        "feedback/feedback.json": {
            "videoId": video_id,
            "status": "feedback_generated",
            "movement": "squat",
            "summary": "Resumo tecnico.",
            "strengths": ["Boa simetria."],
            "improvements": ["Melhorar profundidade."],
            "recommendations": ["Trabalhe mobilidade."],
        },
    }


@pytest.fixture
def stored_video(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[str, Path]:
    video_id = str(uuid4())
    uploads = tmp_path / "uploads"
    outputs = tmp_path / "outputs"
    uploads.mkdir()
    (uploads / f"{video_id}.mp4").write_bytes(b"video")

    monkeypatch.setattr(video_service, "UPLOAD_DIR", uploads)
    monkeypatch.setattr(analysis_service, "OUTPUT_DIR", outputs)
    monkeypatch.setattr(
        analysis_service,
        "process_video",
        lambda stored_id: {
            "videoId": stored_id,
            "status": "processed",
            "metadata": {
                "durationSeconds": 12.5,
                "fps": 30.0,
                "totalFrames": 375,
                "resolution": {"width": 1080, "height": 1920},
                "fileSizeMb": 9.4,
            },
        },
    )
    return video_id, outputs


def _write_artifacts(outputs: Path, video_id: str, omit: str | None = None) -> None:
    for relative_path, data in _artifacts(video_id).items():
        if relative_path == omit:
            continue
        path = outputs / video_id / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")


def test_get_analysis_returns_consolidated_real_result(
    stored_video: tuple[str, Path],
) -> None:
    video_id, outputs = stored_video
    _write_artifacts(outputs, video_id)

    response = client.get(f"/videos/{video_id}/analysis")

    assert response.status_code == 200
    body = response.json()
    assert body["videoId"] == video_id
    assert body["status"] == "completed"
    assert body["movement"] == "squat"
    assert body["metadata"]["durationSeconds"] == 12.5
    assert body["metrics"]["minKneeAngle"] == 82.07
    assert body["totalReps"] == 1
    assert body["reps"][0]["rep"] == 1
    assert body["score"]["overallScore"] == 79
    assert body["score"]["final_score"] == 79
    assert body["score"]["analysis_confidence"] == 91
    assert body["score"]["components"][0]["name"] == "mobility"
    assert body["score"]["score_method"] == "AXON_MOVEMENT_SCORE"
    assert body["score"]["score_version"] == "1.0.0"
    assert body["feedback"]["summary"] == "Resumo tecnico."


def test_get_analysis_returns_not_found_for_unknown_video() -> None:
    response = client.get(f"/videos/{uuid4()}/analysis")

    assert response.status_code == 404
    assert response.json()["detail"] == "Video nao encontrado."


@pytest.mark.parametrize(
    "missing_path",
    [
        "metrics/metrics.json",
        "movement/movement_analysis.json",
        "score/scoring.json",
        "feedback/feedback.json",
    ],
)
def test_get_analysis_requires_all_artifacts(
    stored_video: tuple[str, Path],
    missing_path: str,
) -> None:
    video_id, outputs = stored_video
    _write_artifacts(outputs, video_id, omit=missing_path)

    response = client.get(f"/videos/{video_id}/analysis")

    assert response.status_code == 404
    assert "Conclua o pipeline" in response.json()["detail"]


def test_get_analysis_rejects_invalid_artifact(
    stored_video: tuple[str, Path],
) -> None:
    video_id, outputs = stored_video
    _write_artifacts(outputs, video_id)
    score_path = outputs / video_id / "score" / "scoring.json"
    score_path.write_text("{invalid-json", encoding="utf-8")

    response = client.get(f"/videos/{video_id}/analysis")

    assert response.status_code == 400
    assert response.json()["detail"] == "Resultado processado invalido."


def test_get_analysis_rejects_artifacts_from_another_video(
    stored_video: tuple[str, Path],
) -> None:
    video_id, outputs = stored_video
    _write_artifacts(outputs, video_id)
    feedback_path = outputs / video_id / "feedback" / "feedback.json"
    feedback = json.loads(feedback_path.read_text(encoding="utf-8"))
    feedback["videoId"] = str(uuid4())
    feedback_path.write_text(json.dumps(feedback), encoding="utf-8")

    response = client.get(f"/videos/{video_id}/analysis")

    assert response.status_code == 400
    assert response.json()["detail"] == "Resultado processado invalido."


def test_get_analysis_propagates_metadata_processing_error(
    stored_video: tuple[str, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    video_id, outputs = stored_video
    _write_artifacts(outputs, video_id)

    def fail_metadata_processing(_: str) -> dict:
        raise HTTPException(
            status_code=400,
            detail="Nao foi possivel abrir o video para processamento.",
        )

    monkeypatch.setattr(analysis_service, "process_video", fail_metadata_processing)

    response = client.get(f"/videos/{video_id}/analysis")

    assert response.status_code == 400
    assert "abrir o video" in response.json()["detail"]


def test_analysis_routes_only_expose_real_get() -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert "get" in paths["/videos/{video_id}/analysis"]
    assert "/videos/{video_id}/analyze" not in paths
