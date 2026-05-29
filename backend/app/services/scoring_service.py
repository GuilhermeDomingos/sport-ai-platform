import json
import statistics
from pathlib import Path

from fastapi import HTTPException, status

from app.core.config import OUTPUT_DIR
from app.modules.scoring.engine import calculate_score as calculate_axon_score
from app.modules.scoring.schemas import ScoringInput
from app.schemas.camera_schema import CameraView
from app.services.camera_view_validation_service import (
    ensure_camera_view_allowed,
    get_or_create_camera_view_validation,
    load_camera_view_validation,
)
from app.services.video_service import get_video_info


DEPTH_SCORES = {
    "below_parallel": 95,
    "parallel": 80,
    "above_parallel": 50,
}


def _bounded_score(value: float) -> int:
    return round(max(0.0, min(100.0, value)))


def _load_movement_analysis(video_id: str) -> dict:
    movement_file = OUTPUT_DIR / video_id / "movement" / "movement_analysis.json"
    if not movement_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movement analysis nao encontrado. Execute movement analysis antes.",
        )

    try:
        with movement_file.open("r", encoding="utf-8") as source:
            analysis = json.load(source)
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel ler a analise de movimento para calcular score.",
        ) from exc

    if not isinstance(analysis.get("reps"), list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analise de movimento invalida para calcular score.",
        )
    return analysis


def _load_metrics(video_id: str) -> dict:
    metrics_file = OUTPUT_DIR / video_id / "metrics" / "metrics.json"
    if not metrics_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metricas nao encontradas. Execute metrics calculation antes.",
        )

    try:
        with metrics_file.open("r", encoding="utf-8") as source:
            payload = json.load(source)
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel ler as metricas para calcular score.",
        ) from exc

    metrics = payload.get("metrics")
    if not isinstance(metrics, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Metricas invalidas para calcular score.",
        )
    return payload


def _load_json_file(path: Path, missing_detail: str) -> dict:
    if not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=missing_detail,
        )
    try:
        with path.open("r", encoding="utf-8") as source:
            return json.load(source)
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel ler os artefatos para calcular score.",
        ) from exc


def _pose_quality(video_id: str, valid_reps: int) -> dict:
    payload = _load_json_file(
        OUTPUT_DIR / video_id / "pose" / "landmarks.json",
        "Landmarks nao encontrados. Execute pose detection antes.",
    )

    frames = payload.get("frames", [])
    if not isinstance(frames, list) or not frames:
        return {
            "valid_pose_frame_ratio": 0.0,
            "average_landmark_visibility": 0.0,
            "critical_landmark_visibility_ratio": 0.0,
            "valid_reps": valid_reps,
        }

    critical_names = {
        "left_shoulder",
        "right_shoulder",
        "left_hip",
        "right_hip",
        "left_knee",
        "right_knee",
        "left_ankle",
        "right_ankle",
        "left_foot_index",
        "right_foot_index",
    }
    pose_frames = [frame for frame in frames if frame.get("poseDetected")]
    visibilities: list[float] = []
    critical_visible = 0
    critical_total = len(pose_frames) * len(critical_names)

    for frame in pose_frames:
        landmarks = frame.get("landmarks", [])
        if not isinstance(landmarks, list):
            continue
        for landmark in landmarks:
            visibility = float(landmark.get("visibility", 0.0))
            visibilities.append(visibility)
            if landmark.get("name") in critical_names and visibility >= 0.5:
                critical_visible += 1

    return {
        "valid_pose_frame_ratio": len(pose_frames) / len(frames),
        "average_landmark_visibility": (
            statistics.mean(visibilities) if visibilities else 0.0
        ),
        "critical_landmark_visibility_ratio": (
            critical_visible / critical_total if critical_total else 0.0
        ),
        "valid_reps": valid_reps,
    }


def _load_pose_frames(video_id: str) -> list[dict]:
    payload = _load_json_file(
        OUTPUT_DIR / video_id / "pose" / "landmarks.json",
        "Landmarks nao encontrados. Execute pose detection antes.",
    )
    frames = payload.get("frames", [])
    return frames if isinstance(frames, list) else []


def calculate_depth_score(reps: list[dict]) -> int:
    if not reps:
        return 0

    depth_values = [DEPTH_SCORES.get(rep.get("depth"), 0) for rep in reps]
    penalty = statistics.pstdev(depth_values) * 0.2 if len(reps) > 1 else 0
    return _bounded_score(statistics.mean(depth_values) - penalty)


def calculate_stability_score(reps: list[dict]) -> int:
    if not reps:
        return 0
    return _bounded_score(statistics.mean(rep.get("stabilityScore", 0) for rep in reps))


def calculate_symmetry_score(reps: list[dict]) -> int:
    if not reps:
        return 0

    values = [
        rep.get("symmetryScore", rep.get("stabilityScore", 0)) for rep in reps
    ]
    return _bounded_score(statistics.mean(values))


def calculate_consistency_score(reps: list[dict]) -> int:
    if not reps:
        return 0
    if len(reps) == 1:
        return 100

    angles = [rep.get("minKneeAngle", 0) for rep in reps]
    depths = [DEPTH_SCORES.get(rep.get("depth"), 0) for rep in reps]
    stability = [rep.get("stabilityScore", 0) for rep in reps]
    penalty = (
        statistics.pstdev(angles) * 2
        + statistics.pstdev(depths) * 0.5
        + statistics.pstdev(stability)
    )
    return _bounded_score(100 - penalty)


def calculate_overall_score(
    depth_score: int,
    stability_score: int,
    symmetry_score: int,
    consistency_score: int,
) -> int:
    return _bounded_score(
        depth_score * 0.30
        + stability_score * 0.25
        + symmetry_score * 0.20
        + consistency_score * 0.25
    )


def calculate_score(video_id: str) -> dict:
    video_info = get_video_info(video_id)
    normalized_id = video_info["videoId"]
    metrics_payload = _load_metrics(normalized_id)
    movement_analysis = _load_movement_analysis(normalized_id)
    reps = movement_analysis["reps"]
    camera_view = CameraView(video_info.get("cameraView", CameraView.FRONT.value))
    camera_view_validation = load_camera_view_validation(normalized_id)
    if camera_view_validation is None:
        camera_view_validation = get_or_create_camera_view_validation(
            normalized_id, camera_view, _load_pose_frames(normalized_id)
        )
    ensure_camera_view_allowed(camera_view_validation)

    depth_score = calculate_depth_score(reps)
    stability_score = calculate_stability_score(reps)
    symmetry_score = calculate_symmetry_score(reps)
    consistency_score = calculate_consistency_score(reps)
    legacy_score = {
        "overallScore": calculate_overall_score(
            depth_score, stability_score, symmetry_score, consistency_score
        ),
        "depthScore": depth_score,
        "stabilityScore": stability_score,
        "symmetryScore": symmetry_score,
        "consistencyScore": consistency_score,
    }
    score_result = calculate_axon_score(
        ScoringInput(
            analysis_id=normalized_id,
            exercise_type=movement_analysis.get("movement", "squat"),
            camera_view=camera_view,
            camera_view_validation=camera_view_validation,
            metrics=metrics_payload["metrics"],
            reps=reps,
            pose_quality=_pose_quality(normalized_id, len(reps)),
        )
    )
    axon_score = score_result.model_dump()
    score = {
        **legacy_score,
        **axon_score,
        "overallScore": score_result.final_score,
    }
    result = {
        "videoId": normalized_id,
        "status": "score_calculated",
        "movement": movement_analysis.get("movement", "squat"),
        "camera_view": camera_view.value,
        "camera_view_validation": camera_view_validation.model_dump(mode="json"),
        "score": score,
    }

    output_dir = OUTPUT_DIR / normalized_id / "score"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "scoring.json"
    with output_file.open("w", encoding="utf-8") as output:
        json.dump(result, output, ensure_ascii=True, indent=2)

    return result
