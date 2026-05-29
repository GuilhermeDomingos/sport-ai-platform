import json
import re
import statistics

from fastapi import HTTPException, status

from app.core.config import OUTPUT_DIR
from app.modules.biomechanics.lateral_metrics import build_lateral_measurements
from app.schemas.camera_schema import CameraView
from app.services.camera_view_validation_service import (
    ensure_camera_view_allowed,
    get_or_create_camera_view_validation,
)
from app.services.biomechanics_service import DEPTH_TOLERANCE, calculate_angle
from app.services.video_service import get_video_info


LOCKOUT_ANGLE = 160
VALID_REP_MIN_ANGLE = 120
REQUIRED_LANDMARKS = {
    "left_hip",
    "left_knee",
    "left_ankle",
    "right_hip",
    "right_knee",
    "right_ankle",
}


def _bounded_score(value: float) -> int:
    return round(max(0.0, min(100.0, value)))


def _frame_number(frame: dict, fallback: int) -> int:
    match = re.search(r"(\d+)", frame.get("frame", ""))
    return int(match.group(1)) if match else fallback


def _midpoint_y(left: dict, right: dict) -> float:
    return (left["y"] + right["y"]) / 2


def _depth_classification(depth_offset: float) -> str:
    if depth_offset > DEPTH_TOLERANCE:
        return "below_parallel"
    if depth_offset >= -DEPTH_TOLERANCE:
        return "parallel"
    return "above_parallel"


def _load_landmarks(video_id: str) -> list[dict]:
    landmarks_file = OUTPUT_DIR / video_id / "pose" / "landmarks.json"
    if not landmarks_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Landmarks nao encontrados. Execute pose detection antes.",
        )

    try:
        with landmarks_file.open("r", encoding="utf-8") as source:
            return json.load(source).get("frames", [])
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel ler os landmarks para analisar o movimento.",
        ) from exc


def _build_measurements(frames: list[dict]) -> list[dict]:
    measurements: list[dict] = []
    for fallback, frame in enumerate(frames, start=1):
        if not frame.get("poseDetected"):
            continue

        points = {
            landmark["name"]: landmark for landmark in frame.get("landmarks", [])
        }
        if not REQUIRED_LANDMARKS.issubset(points):
            continue

        try:
            left_knee_angle = calculate_angle(
                points["left_hip"], points["left_knee"], points["left_ankle"]
            )
            right_knee_angle = calculate_angle(
                points["right_hip"], points["right_knee"], points["right_ankle"]
            )
        except ValueError:
            continue

        measurements.append(
            {
                "frame": _frame_number(frame, fallback),
                "kneeAngle": (left_knee_angle + right_knee_angle) / 2,
                "kneeDifference": abs(left_knee_angle - right_knee_angle),
                "kneeTracking": (
                    points["left_knee"]["x"] - points["left_ankle"]["x"]
                )
                - (points["right_knee"]["x"] - points["right_ankle"]["x"]),
                "depthOffset": _midpoint_y(
                    points["left_hip"], points["right_hip"]
                )
                - _midpoint_y(points["left_knee"], points["right_knee"]),
            }
        )
    return measurements


def _finalize_rep(rep_number: int, samples: list[dict], bottom: dict) -> dict:
    start = samples[0]
    end = samples[-1]
    duration_frames = max(1, end["frame"] - start["frame"])
    angular_travel = abs(start["kneeAngle"] - bottom["kneeAngle"]) + abs(
        end["kneeAngle"] - bottom["kneeAngle"]
    )
    knee_tracking = [sample.get("kneeTracking", 0) for sample in samples]
    stability_penalty = (
        statistics.pstdev(knee_tracking) * 500 if len(knee_tracking) > 1 else 0
    )

    return {
        "rep": rep_number,
        "startFrame": start["frame"],
        "bottomFrame": bottom["frame"],
        "endFrame": end["frame"],
        "depth": _depth_classification(bottom["depthOffset"]),
        "minKneeAngle": round(bottom["kneeAngle"], 2),
        "stabilityScore": _bounded_score(100 - stability_penalty),
        "symmetryScore": _bounded_score(
            100 - statistics.mean(sample["kneeDifference"] for sample in samples)
        ),
        "durationFrames": duration_frames,
        "averageVelocity": round(angular_travel / duration_frames, 2),
    }


def _detect_reps(measurements: list[dict]) -> list[dict]:
    reps: list[dict] = []
    state = "standing"
    last_lockout: dict | None = None
    current_rep: list[dict] | None = None
    bottom: dict | None = None

    for measurement in measurements:
        knee_angle = measurement["kneeAngle"]

        if current_rep is None:
            if knee_angle >= LOCKOUT_ANGLE:
                state = "lockout"
                last_lockout = measurement
            elif state == "lockout" and last_lockout is not None:
                state = "descending"
                current_rep = [last_lockout, measurement]
                bottom = measurement
            continue

        current_rep.append(measurement)
        if bottom is None or knee_angle < bottom["kneeAngle"]:
            bottom = measurement
            state = "descending"
        elif knee_angle > bottom["kneeAngle"]:
            state = "ascending"

        if knee_angle >= LOCKOUT_ANGLE:
            state = "lockout"
            if bottom is not None and bottom["kneeAngle"] < VALID_REP_MIN_ANGLE:
                reps.append(_finalize_rep(len(reps) + 1, current_rep, bottom))
            last_lockout = measurement
            current_rep = None
            bottom = None

    return reps


def _finalize_lateral_rep(rep_number: int, samples: list[dict], bottom: dict) -> dict:
    start = samples[0]
    end = samples[-1]
    duration_frames = max(1, end["frame"] - start["frame"])
    angular_travel = abs(start["kneeAngle"] - bottom["kneeAngle"]) + abs(
        end["kneeAngle"] - bottom["kneeAngle"]
    )
    trunk_values = [sample.get("trunkInclination", 0) for sample in samples]
    hip_values = [sample.get("hipY", 0) for sample in samples]
    stability_penalty = (
        statistics.pstdev(trunk_values) * 2 if len(trunk_values) > 1 else 0
    )
    smoothness_penalty = (
        statistics.pstdev(hip_values) * 800 if len(hip_values) > 1 else 0
    )

    return {
        "rep": rep_number,
        "startFrame": start["frame"],
        "bottomFrame": bottom["frame"],
        "endFrame": end["frame"],
        "depth": _depth_classification(bottom["depthOffset"]),
        "minKneeAngle": round(bottom["kneeAngle"], 2),
        "stabilityScore": _bounded_score(100 - stability_penalty - smoothness_penalty),
        "symmetryScore": None,
        "durationFrames": duration_frames,
        "averageVelocity": round(angular_travel / duration_frames, 2),
        "bottomTrunkInclination": round(bottom.get("trunkInclination", 0), 2),
        "minHipAngle": round(
            min(sample.get("hipAngle", 180) for sample in samples),
            2,
        ),
    }


def _detect_lateral_reps(measurements: list[dict]) -> list[dict]:
    reps: list[dict] = []
    state = "standing"
    last_lockout: dict | None = None
    current_rep: list[dict] | None = None
    bottom: dict | None = None

    for measurement in measurements:
        knee_angle = measurement["kneeAngle"]

        if current_rep is None:
            if knee_angle >= LOCKOUT_ANGLE:
                state = "lockout"
                last_lockout = measurement
            elif state == "lockout" and last_lockout is not None:
                state = "descending"
                current_rep = [last_lockout, measurement]
                bottom = measurement
            continue

        current_rep.append(measurement)
        if bottom is None or knee_angle < bottom["kneeAngle"]:
            bottom = measurement
            state = "descending"
        elif knee_angle > bottom["kneeAngle"]:
            state = "ascending"

        if knee_angle >= LOCKOUT_ANGLE:
            state = "lockout"
            if bottom is not None and bottom["kneeAngle"] < VALID_REP_MIN_ANGLE:
                reps.append(_finalize_lateral_rep(len(reps) + 1, current_rep, bottom))
            last_lockout = measurement
            current_rep = None
            bottom = None

    return reps


def analyze_movement(video_id: str) -> dict:
    video_info = get_video_info(video_id)
    normalized_id = video_info["videoId"]
    frames = _load_landmarks(normalized_id)
    camera_view = CameraView(video_info.get("cameraView", CameraView.FRONT.value))
    camera_view_validation = get_or_create_camera_view_validation(
        normalized_id, camera_view, frames
    )
    ensure_camera_view_allowed(camera_view_validation)

    if camera_view is CameraView.SIDE:
        measurements, visible_side = build_lateral_measurements(frames)
    else:
        measurements = _build_measurements(frames)
        visible_side = None

    if not measurements:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao ha landmarks suficientes para analisar o movimento.",
        )

    reps = (
        _detect_lateral_reps(measurements)
        if camera_view is CameraView.SIDE
        else _detect_reps(measurements)
    )
    result = {
        "videoId": normalized_id,
        "movement": video_info.get("exerciseType", "squat"),
        "camera_view": camera_view.value,
        "camera_view_validation": camera_view_validation.model_dump(mode="json"),
        "totalReps": len(reps),
        "reps": reps,
    }
    if visible_side:
        result["visibleSide"] = visible_side

    output_dir = OUTPUT_DIR / normalized_id / "movement"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "movement_analysis.json"
    with output_file.open("w", encoding="utf-8") as output:
        json.dump(result, output, ensure_ascii=True, indent=2)

    return result
