import math
import statistics
from typing import Any, Literal


CRITICAL_LANDMARKS = ("shoulder", "hip", "knee", "ankle", "foot_index")


def _visibility(point: dict[str, Any] | None) -> float:
    if not point:
        return 0.0
    try:
        return float(point.get("visibility", 0.0))
    except (TypeError, ValueError):
        return 0.0


def _point(points: dict[str, dict[str, Any]], side: str, name: str) -> dict[str, Any] | None:
    return points.get(f"{side}_{name}")


def _mean(values: list[float], default: float = 0.0) -> float:
    return statistics.mean(values) if values else default


def _pstdev(values: list[float]) -> float:
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def _clamp_ratio(value: float) -> float:
    return max(0.0, min(1.0, value))


def _bounded_score(value: float) -> int:
    return round(max(0.0, min(100.0, value)))


def calculate_angle(a: dict[str, Any], b: dict[str, Any], c: dict[str, Any]) -> float:
    ba = (float(a["x"]) - float(b["x"]), float(a["y"]) - float(b["y"]))
    bc = (float(c["x"]) - float(b["x"]), float(c["y"]) - float(b["y"]))
    magnitude = math.hypot(*ba) * math.hypot(*bc)
    if magnitude == 0:
        raise ValueError("Nao e possivel calcular angulo com pontos coincidentes.")
    cosine = (ba[0] * bc[0] + ba[1] * bc[1]) / magnitude
    return math.degrees(math.acos(max(-1.0, min(1.0, cosine))))


def calculate_trunk_inclination(shoulder: dict[str, Any], hip: dict[str, Any]) -> float:
    dx = float(shoulder["x"]) - float(hip["x"])
    dy = float(hip["y"]) - float(shoulder["y"])
    return math.degrees(math.atan2(abs(dx), abs(dy)))


def detect_visible_side(pose_frames: list[dict[str, Any]]) -> Literal["left", "right"]:
    side_scores: dict[str, dict[str, float]] = {
        "left": {"visibility": 0.0, "present": 0.0, "total": 0.0},
        "right": {"visibility": 0.0, "present": 0.0, "total": 0.0},
    }

    for frame in pose_frames:
        if not frame.get("poseDetected"):
            continue
        points = {
            landmark.get("name"): landmark
            for landmark in frame.get("landmarks", [])
            if isinstance(landmark, dict)
        }
        for side in ("left", "right"):
            for name in CRITICAL_LANDMARKS:
                side_scores[side]["total"] += 1
                landmark = _point(points, side, name)
                visibility = _visibility(landmark)
                side_scores[side]["visibility"] += visibility
                if landmark is not None:
                    side_scores[side]["present"] += 1

    def side_key(side: str) -> tuple[float, float]:
        total = side_scores[side]["total"] or 1.0
        return (
            side_scores[side]["visibility"] / total,
            side_scores[side]["present"] / total,
        )

    return "left" if side_key("left") >= side_key("right") else "right"


def moving_average(values: list[float], window: int = 3) -> list[float]:
    if window <= 1 or len(values) <= 2:
        return values
    smoothed: list[float] = []
    radius = window // 2
    for index in range(len(values)):
        start = max(0, index - radius)
        end = min(len(values), index + radius + 1)
        smoothed.append(statistics.mean(values[start:end]))
    return smoothed


def build_lateral_measurements(
    pose_frames: list[dict[str, Any]], visible_side: Literal["left", "right"] | None = None
) -> tuple[list[dict[str, Any]], Literal["left", "right"]]:
    side = visible_side or detect_visible_side(pose_frames)
    raw_measurements: list[dict[str, Any]] = []

    for fallback, frame in enumerate(pose_frames, start=1):
        if not frame.get("poseDetected"):
            continue
        points = {
            landmark.get("name"): landmark
            for landmark in frame.get("landmarks", [])
            if isinstance(landmark, dict)
        }
        shoulder = _point(points, side, "shoulder")
        hip = _point(points, side, "hip")
        knee = _point(points, side, "knee")
        ankle = _point(points, side, "ankle")
        foot = _point(points, side, "foot_index")
        if not all([shoulder, hip, knee, ankle]):
            continue

        try:
            knee_angle = calculate_angle(hip, knee, ankle)
            hip_angle = calculate_angle(shoulder, hip, knee)
            trunk_inclination = calculate_trunk_inclination(shoulder, hip)
        except (KeyError, TypeError, ValueError):
            continue

        raw_measurements.append(
            {
                "frame": fallback,
                "kneeAngle": knee_angle,
                "hipAngle": hip_angle,
                "trunkInclination": trunk_inclination,
                "hipY": float(hip["y"]),
                "kneeY": float(knee["y"]),
                "depthOffset": float(hip["y"]) - float(knee["y"]),
                "landmarkConfidence": _mean(
                    [
                        _visibility(shoulder),
                        _visibility(hip),
                        _visibility(knee),
                        _visibility(ankle),
                        _visibility(foot),
                    ]
                ),
            }
        )

    if not raw_measurements:
        return [], side

    for key in ("kneeAngle", "hipAngle", "trunkInclination", "hipY"):
        values = moving_average([float(item[key]) for item in raw_measurements])
        for item, value in zip(raw_measurements, values, strict=True):
            item[key] = value
            if key == "hipY":
                item["depthOffset"] = value - float(item["kneeY"])

    return raw_measurements, side


def _depth_classification(depth_offset: float) -> str:
    if depth_offset > 0.03:
        return "below_parallel"
    if depth_offset >= -0.03:
        return "parallel"
    return "above_parallel"


def calculate_lateral_metrics(
    pose_frames: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    measurements, visible_side = build_lateral_measurements(pose_frames)
    if not measurements:
        return {}, []

    knee_angles = [float(item["kneeAngle"]) for item in measurements]
    hip_angles = [float(item["hipAngle"]) for item in measurements]
    trunk = [float(item["trunkInclination"]) for item in measurements]
    hip_y = [float(item["hipY"]) for item in measurements]
    confidences = [float(item["landmarkConfidence"]) for item in measurements]
    deepest = min(measurements, key=lambda item: item["kneeAngle"])
    knee_rom = max(knee_angles) - min(knee_angles)
    hip_rom = max(hip_angles) - min(hip_angles)
    hip_displacement = max(hip_y) - min(hip_y)
    valid_pose_ratio = len(measurements) / max(1, len(pose_frames))
    critical_visibility = _clamp_ratio(_mean(confidences))
    smoothness_penalty = _pstdev(
        [
            abs(hip_y[index] - hip_y[index - 1])
            for index in range(1, len(hip_y))
        ]
    )
    movement_smoothness = _bounded_score(100 - smoothness_penalty * 1600)
    bottom_window = [
        item
        for item in measurements
        if abs(float(item["kneeAngle"]) - float(deepest["kneeAngle"])) <= 8
    ]
    bottom_control = _bounded_score(
        100
        - _pstdev([float(item["trunkInclination"]) for item in bottom_window]) * 3
        - _pstdev([float(item["hipY"]) for item in bottom_window]) * 800
    )

    squat_depth_ratio = _clamp_ratio((180 - min(knee_angles)) / 95)
    metrics = {
        "averageKneeAngle": round(_mean(knee_angles), 2),
        "minKneeAngle": round(min(knee_angles), 2),
        "averageHipAngle": round(_mean(hip_angles), 2),
        "torsoInclination": round(_mean(trunk), 2),
        "depthClassification": _depth_classification(float(deepest["depthOffset"])),
        "symmetryScore": 100,
        "stabilityScore": bottom_control,
        "cameraView": "side",
        "visibleSide": visible_side,
        "squat_depth_ratio": round(squat_depth_ratio, 3),
        "min_hip_angle": round(min(hip_angles), 2),
        "max_knee_angle": round(max(knee_angles), 2),
        "max_hip_angle": round(max(hip_angles), 2),
        "knee_rom": round(knee_rom, 2),
        "hip_rom": round(hip_rom, 2),
        "hip_vertical_displacement": round(hip_displacement, 4),
        "range_of_motion": round((knee_rom + hip_rom) / 2, 2),
        "max_trunk_inclination": round(max(trunk), 2),
        "bottom_trunk_inclination": round(float(deepest["trunkInclination"]), 2),
        "trunk_variation": round(_pstdev(trunk), 2),
        "movement_smoothness": movement_smoothness,
        "bottom_control": bottom_control,
        "valid_pose_frame_ratio": round(valid_pose_ratio, 3),
        "visible_side_landmark_confidence": round(_mean(confidences), 3),
        "critical_landmarks_visible_ratio": round(critical_visibility, 3),
    }
    return metrics, measurements

