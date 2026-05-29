SCORE_METHOD = "AXON_MOVEMENT_SCORE"
FRONTAL_SCORE_TYPE = "AXON_FRONTAL_MOVEMENT_SCORE"
LATERAL_SCORE_TYPE = "AXON_LATERAL_MOVEMENT_SCORE"
SCORE_VERSION = "1.0.0"

SCORE_WEIGHTS = {
    "squat": {
        "mobility": 0.20,
        "stability": 0.20,
        "symmetry": 0.20,
        "motor_control": 0.25,
        "analysis_confidence": 0.15,
    }
}

SCORE_CONFIG = {
    ("squat", "front"): {
        "score_type": FRONTAL_SCORE_TYPE,
        "score_method": SCORE_METHOD,
        "score_version": SCORE_VERSION,
        "weights": SCORE_WEIGHTS["squat"],
    },
    ("squat", "side"): {
        "score_type": LATERAL_SCORE_TYPE,
        "score_method": LATERAL_SCORE_TYPE,
        "score_version": SCORE_VERSION,
        "weights": {
            "amplitude_depth": 0.25,
            "joint_kinematics": 0.20,
            "trunk_posture": 0.20,
            "motor_control": 0.20,
            "analysis_confidence": 0.15,
        },
    },
}

MIN_CONFIDENCE_TO_SCORE = 40
LOW_CONFIDENCE_WARNING = 60
