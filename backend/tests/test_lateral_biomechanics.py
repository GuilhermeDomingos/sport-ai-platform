from app.modules.biomechanics.lateral_metrics import (
    calculate_lateral_metrics,
    detect_visible_side,
)


def _landmark(name: str, x: float, y: float, visibility: float = 0.95) -> dict:
    return {"name": name, "x": x, "y": y, "z": 0.0, "visibility": visibility}


def _frame(knee_y: float, visibility_left: float = 0.3, visibility_right: float = 0.95) -> dict:
    return {
        "poseDetected": True,
        "landmarks": [
            _landmark("left_shoulder", 0.38, 0.20, visibility_left),
            _landmark("left_hip", 0.40, 0.46, visibility_left),
            _landmark("left_knee", 0.42, knee_y, visibility_left),
            _landmark("left_ankle", 0.44, 0.86, visibility_left),
            _landmark("left_foot_index", 0.48, 0.90, visibility_left),
            _landmark("right_shoulder", 0.58, 0.20, visibility_right),
            _landmark("right_hip", 0.56, 0.46, visibility_right),
            _landmark("right_knee", 0.54, knee_y, visibility_right),
            _landmark("right_ankle", 0.52, 0.86, visibility_right),
            _landmark("right_foot_index", 0.49, 0.90, visibility_right),
        ],
    }


def test_detect_visible_side_uses_landmark_confidence() -> None:
    frames = [_frame(0.62), _frame(0.70)]

    assert detect_visible_side(frames) == "right"


def test_calculate_lateral_metrics_returns_side_specific_fields() -> None:
    frames = [_frame(0.55), _frame(0.68), _frame(0.76), _frame(0.62)]

    metrics, measurements = calculate_lateral_metrics(frames)

    assert measurements
    assert metrics["cameraView"] == "side"
    assert metrics["visibleSide"] == "right"
    assert metrics["knee_rom"] >= 0
    assert metrics["movement_smoothness"] >= 0
    assert metrics["critical_landmarks_visible_ratio"] > 0.8

