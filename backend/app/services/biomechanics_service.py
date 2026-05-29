import json
import math
import statistics

from fastapi import HTTPException, status

from app.core.config import OUTPUT_DIR
from app.modules.biomechanics.lateral_metrics import calculate_lateral_metrics
from app.schemas.camera_schema import CameraView
from app.services.video_service import get_video_info


REQUIRED_LANDMARKS = {
    "left_shoulder",
    "right_shoulder",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
}
DEPTH_TOLERANCE = 0.03


def calculate_angle(a: dict, b: dict, c: dict) -> float:
    ba = (a["x"] - b["x"], a["y"] - b["y"])
    bc = (c["x"] - b["x"], c["y"] - b["y"])
    magnitude = math.hypot(*ba) * math.hypot(*bc)

    if magnitude == 0:
        raise ValueError("Nao e possivel calcular angulo com pontos coincidentes.")

    cosine = (ba[0] * bc[0] + ba[1] * bc[1]) / magnitude
    return math.degrees(math.acos(max(-1.0, min(1.0, cosine))))


def _midpoint(a: dict, b: dict) -> dict[str, float]:
    return {"x": (a["x"] + b["x"]) / 2, "y": (a["y"] + b["y"]) / 2}


def _torso_inclination(shoulders: dict, hips: dict) -> float:
    dx = shoulders["x"] - hips["x"]
    dy = hips["y"] - shoulders["y"]
    return math.degrees(math.atan2(abs(dx), abs(dy)))


def _bounded_score(value: float) -> int:
    return round(max(0.0, min(100.0, value)))


def _load_landmarks(video_id: str) -> list[dict]:
    landmarks_file = OUTPUT_DIR / video_id / "pose" / "landmarks.json"
    if not landmarks_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Landmarks nao encontrados. Detecte a pose antes de calcular metricas.",
        )

    try:
        with landmarks_file.open("r", encoding="utf-8") as source:
            return json.load(source).get("frames", [])
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel ler os landmarks para calcular metricas.",
        ) from exc


def calculate_metrics(video_id: str) -> dict:
    video_info = get_video_info(video_id)
    normalized_id = video_info["videoId"]
    frames = _load_landmarks(normalized_id)
    camera_view = CameraView(video_info.get("cameraView", CameraView.FRONT.value))

    if camera_view is CameraView.SIDE:
        metrics, calculated_frames = calculate_lateral_metrics(frames)
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nao ha landmarks suficientes para calcular metricas laterais.",
            )

        output_dir = OUTPUT_DIR / normalized_id / "metrics"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "metrics.json"
        with output_file.open("w", encoding="utf-8") as output:
            json.dump(
                {
                    "videoId": normalized_id,
                    "movement": video_info.get("exerciseType", "squat"),
                    "camera_view": camera_view.value,
                    "metrics": metrics,
                },
                output,
                ensure_ascii=True,
                indent=2,
            )

        return {
            "videoId": normalized_id,
            "status": "metrics_calculated",
            "movement": video_info.get("exerciseType", "squat"),
            "camera_view": camera_view.value,
            "metrics": metrics,
        }

    calculated_frames: list[dict] = []

    for frame in frames:
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
            left_hip_angle = calculate_angle(
                points["left_shoulder"], points["left_hip"], points["left_knee"]
            )
            right_hip_angle = calculate_angle(
                points["right_shoulder"], points["right_hip"], points["right_knee"]
            )
        except ValueError:
            continue

        hips = _midpoint(points["left_hip"], points["right_hip"])
        knees = _midpoint(points["left_knee"], points["right_knee"])
        shoulders = _midpoint(points["left_shoulder"], points["right_shoulder"])
        calculated_frames.append(
            {
                "kneeAngle": (left_knee_angle + right_knee_angle) / 2,
                "hipAngle": (left_hip_angle + right_hip_angle) / 2,
                "kneeDifference": abs(left_knee_angle - right_knee_angle),
                "torsoInclination": _torso_inclination(shoulders, hips),
                "depthOffset": hips["y"] - knees["y"],
                "leftKneeOffset": points["left_knee"]["x"]
                - points["left_ankle"]["x"],
                "rightKneeOffset": points["right_knee"]["x"]
                - points["right_ankle"]["x"],
            }
        )

    if not calculated_frames:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao ha landmarks suficientes para calcular metricas.",
        )

    knee_angles = [frame["kneeAngle"] for frame in calculated_frames]
    hip_angles = [frame["hipAngle"] for frame in calculated_frames]
    deepest_frame = min(calculated_frames, key=lambda frame: frame["kneeAngle"])
    depth_offset = deepest_frame["depthOffset"]
    if depth_offset > DEPTH_TOLERANCE:
        depth_classification = "below_parallel"
    elif depth_offset >= -DEPTH_TOLERANCE:
        depth_classification = "parallel"
    else:
        depth_classification = "above_parallel"

    symmetry_penalty = statistics.mean(
        frame["kneeDifference"] for frame in calculated_frames
    )
    knee_tracking = [
        frame["leftKneeOffset"] - frame["rightKneeOffset"]
        for frame in calculated_frames
    ]
    stability_penalty = (
        statistics.pstdev(knee_tracking) * 500 if len(knee_tracking) > 1 else 0
    )

    metrics = {
        "averageKneeAngle": round(statistics.mean(knee_angles), 2),
        "minKneeAngle": round(min(knee_angles), 2),
        "averageHipAngle": round(statistics.mean(hip_angles), 2),
        "torsoInclination": round(
            statistics.mean(
                frame["torsoInclination"] for frame in calculated_frames
            ),
            2,
        ),
        "depthClassification": depth_classification,
        "symmetryScore": _bounded_score(100 - symmetry_penalty),
        "stabilityScore": _bounded_score(100 - stability_penalty),
    }

    output_dir = OUTPUT_DIR / normalized_id / "metrics"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "metrics.json"
    with output_file.open("w", encoding="utf-8") as output:
        json.dump(
            {
                "videoId": normalized_id,
                "movement": video_info.get("exerciseType", "squat"),
                "camera_view": camera_view.value,
                "metrics": metrics,
            },
            output,
            ensure_ascii=True,
            indent=2,
        )

    return {
        "videoId": normalized_id,
        "status": "metrics_calculated",
        "movement": video_info.get("exerciseType", "squat"),
        "camera_view": camera_view.value,
        "metrics": metrics,
    }
