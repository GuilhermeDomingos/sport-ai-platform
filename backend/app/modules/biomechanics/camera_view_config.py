CAMERA_VIEW_VALIDATION_CONFIG = {
    "min_confidence_to_block": 70,
    "min_score_diff_to_detect": 15,
    "min_valid_frames": 10,
    "min_landmark_visibility": 0.55,
    # Initial heuristic thresholds.
    # These values must be calibrated with real AXON videos.
    "front": {
        "min_shoulder_width_ratio": 0.16,
        "min_hip_width_ratio": 0.10,
        "max_left_right_confidence_diff": 0.18,
        "min_knee_distance_ratio": 0.10,
        "min_ankle_distance_ratio": 0.10,
    },
    "side": {
        "max_shoulder_width_ratio": 0.13,
        "max_hip_width_ratio": 0.09,
        "min_left_right_confidence_diff": 0.18,
        "max_knee_distance_ratio": 0.08,
        "max_ankle_distance_ratio": 0.08,
        "min_dominant_side_confidence": 0.70,
    },
}
